--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Debian 16.9-1.pgdg120+1)
-- Dumped by pg_dump version 16.9 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, is_admin, full_name) FROM stdin;
1	Yokoyama	scrypt:32768:8:1$EI1JwoDIbZNODliz$bc438e3b4fad1d378ddb6999b56d7eb02b45e0dcdce1b3b638dd69d978552e8d607ce29551f82a94d0dab0b8e41211dc840f594eb388983e65267045b14fd373	t	横山幸咲
5	tatsunami	scrypt:32768:8:1$qfzUkWgAdR9Dq8rY$b3ecdc8de7b86e674c07728071598a75a1f3d049ce3c89f91aa29f93cf1f53c42c1ea71ecea76f904b356afaaf1ee5549f0ad3eacc27f7b92663b8c9edd78526	f	立浪和義
6	yujia	scrypt:32768:8:1$Q30awXKMjaUPWfI4$3cddf8dae13c45b1fa01bd600e6addca7002b6b91c2610ac85394dd59ebc484451cceca9d969a1d8a247449b5aa23197d4532db1944e1cf6d993fd7cea6208d4	f	安藤悠司
7	kouta	scrypt:32768:8:1$EQPkCub6BhgfMZCk$72a593532503e44d182b3bc3b523bb932eb556d73283bb0088652eddd435cf970cec77887d8bec932f2668d467b833cb59b5d583a758fb916bdff9b5bbcfbf78	f	北川航太
\.


--
-- Data for Name: shift_entries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shift_entries (date_str, staff_name, status, user_id) FROM stdin;
2025-06-19	昼		5
2025-06-19	夜		5
2025-06-20	昼		5
2025-06-20	夜		5
2025-06-21	昼		5
2025-06-21	夜		5
2025-06-22	昼		5
2025-06-22	夜		5
2025-06-23	昼		5
2025-06-23	夜		5
2025-06-26	昼		5
2025-06-26	夜		5
2025-06-27	昼		5
2025-06-27	夜		5
2025-06-28	昼		5
2025-06-28	夜		5
2025-06-29	昼		5
2025-06-29	夜		5
2025-06-30	昼		5
2025-06-30	夜		5
2025-07-13	昼		6
2025-07-13	夜		6
2025-07-06	夜	○	7
2025-07-06	昼		7
2025-07-07	夜		7
2025-07-07	昼		7
2025-07-10	夜	○	7
2025-07-13	夜	○	7
2025-07-17	夜	○	7
2025-07-10	昼		7
2025-07-11	昼		7
2025-07-11	夜		7
2025-07-12	昼		7
2025-07-12	夜		7
2025-07-13	昼		7
2025-07-14	昼		7
2025-07-14	夜		7
2025-07-17	昼		7
2025-07-18	昼		7
2025-07-18	夜		7
2025-07-19	昼		7
2025-07-19	夜		7
2025-07-03	昼		6
2025-07-03	夜		6
2025-07-04	昼		6
2025-07-04	夜		6
2025-07-05	夜		6
2025-07-03	昼		1
2025-07-03	夜		1
2025-07-04	夜		1
2025-07-05	昼		1
2025-07-07	昼		1
2025-07-07	夜		1
2025-07-10	昼		1
2025-07-10	夜		1
2025-07-11	夜		1
2025-07-12	昼		1
2025-07-13	昼		1
2025-07-14	昼		1
2025-07-14	夜		1
2025-07-04	昼	○	1
2025-07-05	夜		1
2025-07-06	夜	○	1
2025-07-06	昼	○	1
2025-07-11	昼	○	1
2025-07-12	夜	○	1
2025-07-13	夜	○	1
2025-07-10	昼		6
2025-07-10	夜		6
2025-07-11	昼		6
2025-07-11	夜		6
2025-07-12	昼		6
2025-07-14	夜		6
2025-07-05	昼	○	6
2025-07-06	昼	○	6
2025-07-06	夜	○	6
2025-07-07	夜	○	6
2025-07-07	昼		6
2025-07-12	夜	○	6
2025-07-14	昼	○	6
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

