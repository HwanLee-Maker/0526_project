from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect
)

import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'secret123'

DATABASE = 'database.db'


# -----------------------------------
# DB 연결
# -----------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------------
# 샘플 데이터 생성
# -----------------------------------
def generate_sample_contacts():

    last_names = ['김', '이', '박', '최', '정']
    first_names = [
        '민수', '서준', '지호',
        '하은', '서연', '지민'
    ]

    mbtis = [
        'INTJ', 'ENFP',
        'ISTP', 'INFJ',
        'ESTJ', 'ISFP'
    ]

    addresses = [
        '서울 강남구',
        '서울 송파구',
        '서울 마포구',
        '경기 수원시',
        '경기 성남시',
        '인천 연수구',
        '인천 부평구'
    ]

    genders = ['남', '여']

    contacts = []

    for i in range(50):

        name = (
            random.choice(last_names)
            + random.choice(first_names)
        )

        gender = random.choice(genders)

        age = random.randint(20, 40)

        address = random.choice(addresses)

        mbti = random.choice(mbtis)

        contacts.append(
            (name, gender, age, address, mbti)
        )

    return contacts


# -----------------------------------
# DB 초기화
# -----------------------------------
def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    # users 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    ''')

    # contacts 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            age INTEGER,
            address TEXT,
            mbti TEXT
        )
    ''')

    # admin 계정 생성
    cursor.execute(
        'SELECT * FROM users WHERE username=?',
        ('admin',)
    )

    admin = cursor.fetchone()

    if not admin:
        cursor.execute('''
            INSERT INTO users (
                username,
                password,
                role
            )
            VALUES (?, ?, ?)
        ''', ('admin', '1234', 'admin'))

    # contacts 샘플 데이터
    cursor.execute(
        'SELECT COUNT(*) FROM contacts'
    )

    count = cursor.fetchone()[0]

    if count == 0:

        sample_contacts = (
            generate_sample_contacts()
        )

        cursor.executemany('''
            INSERT INTO contacts (
                name,
                gender,
                age,
                address,
                mbti
            )
            VALUES (?, ?, ?, ?, ?)
        ''', sample_contacts)

    conn.commit()
    conn.close()


# -----------------------------------
# 로그인 체크 함수
# -----------------------------------
def check_login():

    if 'user' not in session:
        return False

    return True


# -----------------------------------
# 페이지 라우팅
# -----------------------------------

# 메인 페이지
@app.route('/')
def index():

    if not check_login():
        return redirect('/login')

    return render_template(
        'search/index.html'
    )


# 로그인 페이지
@app.route('/login')
def login_page():

    return render_template(
        'auth/login.html'
    )


# -----------------------------------
# 로그인 API
# -----------------------------------
@app.route(
    '/api/login',
    methods=['POST']
)
def login():

    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()

    user = conn.execute('''
        SELECT * FROM users
        WHERE username=?
        AND password=?
    ''', (username, password)).fetchone()

    conn.close()

    # 로그인 성공
    if user:

        session['user'] = username

        return jsonify({
            'success': True,
            'message': '로그인 성공'
        })

    # 로그인 실패
    return jsonify({
        'success': False,
        'message': '아이디 또는 비밀번호 오류'
    })


# -----------------------------------
# 로그아웃 API
# -----------------------------------
@app.route(
    '/api/logout',
    methods=['POST']
)
def logout():

    session.clear()

    return jsonify({
        'success': True
    })


# -----------------------------------
# 연락처 조회 API
# -----------------------------------
@app.route(
    '/api/contacts',
    methods=['GET']
)
def get_contacts():

    if not check_login():

        return jsonify({
            'success': False,
            'message': '로그인 필요'
        }), 401

    q = request.args.get('q', '')

    conn = get_db_connection()

    # 검색어 있으면 LIKE 검색
    if q:

        contacts = conn.execute('''
            SELECT * FROM contacts
            WHERE
                name LIKE ?
                OR address LIKE ?
                OR mbti LIKE ?
        ''', (
            f'%{q}%',
            f'%{q}%',
            f'%{q}%'
        )).fetchall()

    # 전체 조회
    else:

        contacts = conn.execute('''
            SELECT * FROM contacts
            ORDER BY id DESC
        ''').fetchall()

    conn.close()

    result = []

    for contact in contacts:

        result.append({
            'id': contact['id'],
            'name': contact['name'],
            'gender': contact['gender'],
            'age': contact['age'],
            'address': contact['address'],
            'mbti': contact['mbti']
        })

    return jsonify(result)


# -----------------------------------
# 연락처 추가 API
# -----------------------------------
@app.route(
    '/api/contacts',
    methods=['POST']
)
def add_contact():

    if not check_login():

        return jsonify({
            'success': False,
            'message': '로그인 필요'
        }), 401

    data = request.get_json()

    name = data.get('name')
    gender = data.get('gender')
    age = data.get('age')
    address = data.get('address')
    mbti = data.get('mbti')

    conn = get_db_connection()

    conn.execute('''
        INSERT INTO contacts (
            name,
            gender,
            age,
            address,
            mbti
        )
        VALUES (?, ?, ?, ?, ?)
    ''', (
        name,
        gender,
        age,
        address,
        mbti
    ))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': '연락처 추가 완료'
    })


# -----------------------------------
# 서버 실행
# -----------------------------------
if __name__ == '__main__':

    init_db()

    app.run(
        debug=True,
        host='0.0.0.0'
    )