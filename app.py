from flask import Flask, render_template, request, jsonify
from datetime import date, timedelta
import calendar # calendarモジュールは今回は直接使っていませんが、あれば便利です

app = Flask(__name__)

# --- グローバル変数/定数 ---
# ※ このアプリではデータベースを使用するため、スプレッドシートIDは不要です。
#    ただし、将来的にスプレッドシートと連携したい場合は、ここに設定します。

# シフト担当者の名前 (必要に応じて増減)
STAFF_NAMES = ["昼", "夜"]

# --- データベースの設定 (SQLiteを推奨) ---
import sqlite3

DATABASE_NAME = 'shifts.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # テーブルが存在しなければ作成
    # date_str: 日付文字列 (YYYY-MM-DD) PRIMARY KEY
    # staff_name: スタッフ名 PRIMARY KEY
    # status: '○' or ''
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shift_entries (
            date_str TEXT NOT NULL,
            staff_name TEXT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (date_str, staff_name)
        )
    ''')
    conn.commit()
    conn.close()

# アプリ起動時にデータベースを初期化
# app.app_context() の中でのみ実行（リクエストコンテキスト外でDB初期化するため）
with app.app_context():
    init_db()


# --- ヘルパー関数 ---
def get_day_of_week_jp(date_obj):
    """日付オブジェクトから日本語の曜日を取得"""
    # Pythonのweekday()は月曜が0、日曜が6
    weekdays_jp = ["月", "火", "水", "木", "金", "土", "日"]
    return weekdays_jp[date_obj.weekday()]


# --- ルート（URLと関数のマッピング） ---

@app.route('/')
def index():
    """ホーム画面のHTMLをレンダリング"""
    # テンプレートファイル (index.html) を探す場所は 'templates' フォルダ
    return render_template('index.html', staff_names=STAFF_NAMES)


@app.route('/api/initial_data', methods=['GET'])
def get_initial_data():
    """初期データ（デフォルトの開始日）を返すAPI"""
    today = date.today()
    default_start_date = today.isoformat() # 'YYYY-MM-DD' 形式
    return jsonify({'defaultStartDate': default_start_date})


@app.route('/api/generate_shift', methods=['POST'])
def generate_shift():
    """シフト日付を生成し、データをDBに保存（または更新）するAPI"""
    data = request.get_json()
    start_date_str = data.get('startDate')

    if not start_date_str:
        return jsonify({'error': 'シフト開始日を選択してください。'}), 400

    try:
        start_date = date.fromisoformat(start_date_str)
    except ValueError:
        return jsonify({'error': '無効な開始日形式です。YYYY-MM-DD形式で入力してください。'}), 400

    end_date = start_date + timedelta(days=13) # 2週間後まで

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 既存のシフトを削除（指定範囲内の日付全て）
    # 今回の生成ロジックは範囲内のものを全てクリアして再生成するので、
    # 直近2週間のデータだけを対象にしても良いし、完全にクリアしても良い
    # ここでは2週間分の範囲を対象に削除
    cursor.execute("DELETE FROM shift_entries WHERE date_str >= ? AND date_str <= ?", (start_date_str, end_date.isoformat()))

    # 新しいシフトデータを生成し、DBに挿入
    current_date = start_date
    last_written_date_obj = None # 日付オブジェクトとして保持

    while current_date <= end_date:
        day_of_week = current_date.weekday() # 月:0, 火:1, ... 日:6

        # 火曜日（1）と水曜日（2）をスキップ
        if day_of_week == 1 or day_of_week == 2: # Pythonのweekday()は月曜が0
            current_date += timedelta(days=1)
            continue # この日の処理をスキップ

        # データベースに各日付と各スタッフのエントリを初期状態（空）で追加
        for staff in STAFF_NAMES:
            cursor.execute("INSERT INTO shift_entries (date_str, staff_name, status) VALUES (?, ?, ?)",
                          (current_date.isoformat(), staff, '')) # 初期状態は空

        last_written_date_obj = current_date # 最後に書き込んだ日付を更新
        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    return jsonify({'success': 'シフトが正常に生成されました！'})


@app.route('/api/get_shift_data', methods=['GET'])
def get_shift_data():
    """DBから現在のシフトデータを取得し、Webアプリに返すAPI"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT date_str, staff_name, status FROM shift_entries ORDER BY date_str, staff_name")
    rows = cursor.fetchall()
    conn.close()

    shift_data_map = {}
    
    for row in rows:
        date_str, staff_name, status = row
        if date_str not in shift_data_map:
            date_obj = date.fromisoformat(date_str)
            # ★変更点1: 日付のフォーマットを月/日に変更★
            formatted_date = date_obj.strftime('%m/%d') # 例: '07/03'
            
            shift_data_map[date_str] = {
                'date': formatted_date, # フォーマット済みの日付文字列を格納
                'rawDate': date_str,    # DB更新用に元のYYYY-MM-DD形式も保持
                'dayOfWeek': get_day_of_week_jp(date_obj),
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


@app.route('/api/update_checkbox', methods=['POST'])
def update_checkbox():
    """チェックボックスの状態をDBで更新するAPI"""
    data = request.get_json()
    date_str = data.get('date')
    staff_name = data.get('staffName')
    status = data.get('status') # '○' or ''

    if not all([date_str, staff_name, status is not None]):
        return jsonify({'error': '必要なデータが不足しています。'}), 400

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE shift_entries SET status = ? WHERE date_str = ? AND staff_name = ?",
                      (status, date_str, staff_name))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'データベース更新エラー: {e}'}), 500
    finally:
        conn.close()

    return jsonify({'success': 'チェックボックスの状態を更新しました。'})


@app.route('/api/clear_shift', methods=['POST'])
def clear_shift():
    """DBの全シフトデータをクリアするAPI"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM shift_entries")
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'データベースクリアエラー: {e}'}), 500
    finally:
        conn.close()

    return jsonify({'success': 'シフトデータがクリアされました。'})


if __name__ == '__main__':
    # 開発用サーバーを実行
    # debug=True にすると、コード変更時に自動でサーバーが再起動され便利です
    app.run(debug=True)