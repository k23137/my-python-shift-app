from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from datetime import date, timedelta

# 外部ファイルのインポート
from db import get_db_connection
from flask_babel import _, format_date
from config import STAFF_NAMES # config.pyからSTAFF_NAMESをインポート

shifts_bp = Blueprint('shifts', __name__) # Blueprintを作成

@shifts_bp.route('/')
@login_required
def index():
    settings_auth_url = url_for('admin.settings_auth')
    return render_template('index.html', staff_names=STAFF_NAMES, url_for_admin_settings_auth=settings_auth_url)

@shifts_bp.route('/api/initial_data', methods=['GET'])
@login_required
def get_initial_data():
    today = date.today()
    default_start_date = today.isoformat()
    return jsonify({'defaultStartDate': default_start_date})


@shifts_bp.route('/api/generate_shift', methods=['POST'])
@login_required
def generate_shift():
    data = request.get_json()
    start_date_str = data.get('startDate')

    user_id = current_user.id

    if not start_date_str:
        return jsonify({'error': _('シフト開始日を選択してください。')}), 400

    try:
        start_date = date.fromisoformat(start_date_str)
    except ValueError:
        return jsonify({'error': _('無効な開始日形式です。YYYY-MM-DD形式で入力してください。')}), 400

    end_date = start_date + timedelta(days=13)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ★★★ 修正箇所 ★★★
        # 指定期間だけでなく、ユーザーの全シフトデータを削除する
        cursor.execute("DELETE FROM shift_entries WHERE user_id = %s", (user_id,))

        current_date = start_date

        shifts_to_insert = [] 
        last_written_date_obj = None

        while current_date <= end_date:
            day_of_week = current_date.weekday()

            if day_of_week == 1 or day_of_week == 2: # 火曜日（1）と水曜日（2）をスキップ
                current_date += timedelta(days=1)
                continue

            # 月曜日（0）と木曜日（3）の間の空白行を考慮
            if last_written_date_obj and last_written_date_obj.weekday() == 0 and day_of_week == 3:
                # DBには詰めて保存し、取得時にUI側で空行を判断・描画するため、ここでは特別な処理は不要
                pass 
                
            for staff in STAFF_NAMES:
                shifts_to_insert.append((current_date.isoformat(), staff, '', user_id))

            last_written_date_obj = current_date
            current_date += timedelta(days=1)

        if shifts_to_insert:
            cursor.executemany(
                "INSERT INTO shift_entries (date_str, staff_name, status, user_id) VALUES (%s, %s, %s, %s)",
                shifts_to_insert
            )

        conn.commit()
        return jsonify({'success': _('シフトが正常に生成されました！')})
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'error': _('シフト生成エラー: %(error_message)s', error_message=str(e))}), 500
    finally:
        if conn: conn.close()


@shifts_bp.route('/api/get_shift_data', methods=['GET'])
@login_required
def get_shift_data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT date_str, staff_name, status FROM shift_entries WHERE user_id = %s ORDER BY date_str, staff_name", (current_user.id,))
        rows = cursor.fetchall()
    finally:
        if conn: conn.close()

    shift_data_map = {}
    
    for row in rows:
        date_str, staff_name, status = row
        if date_str not in shift_data_map:
            date_obj = date.fromisoformat(date_str)
            formatted_date = format_date(date_obj, format='MM/dd')
            formatted_day_of_week = format_date(date_obj, format='EEE')

            shift_data_map[date_str] = {
                'date': formatted_date,
                'rawDate': date_str,
                'dayOfWeek': formatted_day_of_week,
                'checkboxes': [''] * len(STAFF_NAMES)
            }
        
        try:
            staff_idx = STAFF_NAMES.index(staff_name)
            shift_data_map[date_str]['checkboxes'][staff_idx] = status
        except ValueError:
            pass

    sorted_dates = sorted(shift_data_map.keys())
    final_shift_data = []
    
    last_processed_date_obj = None

    for d_str in sorted_dates:
        current_date_obj = date.fromisoformat(d_str)

        if last_processed_date_obj:
            if last_processed_date_obj.weekday() == 0 and current_date_obj.weekday() == 3:
                final_shift_data.append({
                    'date': '',
                    'dayOfWeek': '',
                    'checkboxes': [''] * len(STAFF_NAMES),
                    'is_empty_row': True
                })
        
        final_shift_data.append(shift_data_map[d_str])
        last_processed_date_obj = current_date_obj

    return jsonify(final_shift_data)


@shifts_bp.route('/api/update_checkbox', methods=['POST'])
@login_required
def update_checkbox():
    data = request.get_json()
    date_str = data.get('date')
    staff_name = data.get('staffName')
    status = data.get('status')
    
    user_id = current_user.id

    if not all([date_str, staff_name, status is not None]):
        return jsonify({'error': _('必要なデータが不足しています。')}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE shift_entries SET status = %s WHERE date_str = %s AND staff_name = %s AND user_id = %s",
                    (status, date_str, staff_name, user_id))
        conn.commit()
        return jsonify({'success': _('チェックボックスの状態を更新しました。')})
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'error': _('データベース更新エラー: %(error_message)s', error_message=str(e))}), 500
    finally:
        if conn: conn.close()


@shifts_bp.route('/api/clear_shift', methods=['POST'])
@login_required
def clear_shift():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM shift_entries WHERE user_id = %s", (current_user.id,))
        conn.commit()
        return jsonify({'success': _('シフトデータがクリアされました。')})
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'error': _('シフトデータクリアエラー: %(error_message)s', error_message=str(e))}), 500
    finally:
        if conn: conn.close()