from pymongo import MongoClient


def get_followers_count(user_name, db_coll):
    """������� ���������� ���������� ����������� ���������� ������������."""
    return db_coll.count_documents({'following': {'$in': [user_name]}})


def print_followers(user_name, db_coll):
    """������� �������� ���� ����������� ���������� ������������"""
    followers = db_coll.find({'following': {'$in': [user_name]}})
    if followers:
        print(f'���������� ������������ {user_name}:')
        for ind, follower in enumerate(followers, 1):
            if follower["full_name"]:
                print(f'{ind}) {follower["full_name"]} (@{follower["name"]})')
            else:
                print(f'{ind}) {follower["name"]}')


def print_following(user_name, following_list, db_coll):
    """������� �������� ��� �������� ���������� ������������"""
    following = db_coll.find({'name': {'$in': following_list}})
    if following:
        print(f'�������� ������������ {user_name}:')
        for ind, follow in enumerate(following, 1):
            if follow["full_name"]:
                print(f'{ind}) {follow["full_name"]} (@{follow["name"]})')
            else:
                print(f'{ind}) {follow["name"]}')


print('��������� ��� ������ � ����� Instagram')
username = input('������� ��� ������������ Instagram: ')

# ��������� ����������� � ���� ������
mongodb_client = MongoClient('localhost', 27017)
mongodb_collection = mongodb_client['gb_instagram']['users']

# ����� ������������ � ������ ����� ����������
user = mongodb_collection.find_one({'name': username})
if user:
    print('���� ���������� �� ���� ������������ � ����� ���� ������!')
    print(f'�����: {user["name"]}. ������ ���: {user["full_name"]}')
    print('���������� �����������:', get_followers_count(username, mongodb_collection))
    print('���������� ��������:', len(user["following"]))
    print('������ ������:')
    print(' 1 - ���������� ���� �����������')
    print(' 2 - ���������� ��� ��������')
    print(' 3 - ���������� ��� ������')
    print(' 0 - �����')
    command = input('������� �������: ')
    if command == '1':
        print_followers(username, mongodb_collection)
    elif command == '2':
        print_following(username, user['following'], mongodb_collection)
    elif command == '3':
        print_followers(username, mongodb_collection)
        print('-' * 50)
        print_following(username, user['following'], mongodb_collection)
else:
    print('������ ������������ � ����� ���� ������ ���.')

# ��������� ����������� � ���� ������
mongodb_client.close()