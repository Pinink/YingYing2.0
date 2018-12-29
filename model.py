#!/usr/bin/python
# -*- coding: utf-8 -*-
import web
import datetime
import util
import hashlib
import settings

# belong to zx & cyh & lsc
# 连接MySQL数据库
db = web.database(dbn='mysql', db='forum', user=settings.MYSQL_USERNAME, pw=settings.MYSQL_PASSWORD)
part_name = ['A', 'B', 'C']
def convert_db_dic(members):
    if not members:
        return None
    lis = []
    for member in members:
        temp = dict()
        for key in member:
            temp[key]=member[key]
        lis.append(temp)
    return lis
class User:
    def new(self, info):
        print("in User\n")
        print(info)
        pwdhash = hashlib.md5(info['password']).hexdigest()
        print("are you here _______")
        return db.insert('users', email=info['email'], name=info['username'], password=pwdhash, nickname = info['nickname'], birthday = info['birthday'],
                         gender = info['gender'], age = info['age'], degree = info['degree'], picture='/static/img/user_normal.jpg', description='',)

    def update(self, id, **kwd):
        try:
            if 'nickname' in kwd and kwd['nickname']:
                db.update('users', where='id = $id', name = kwd['name'], vars = locals())
            if 'birthday' in kwd and kwd['birthday']:
                db.update('users', where='id = $id', birthday = kwd['birthday'], vars = locals())
            if 'gender' in kwd and kwd['gender']:
                db.update('users', where='id = $id', gender = kwd['gender'], vars = locals())
            if 'age' in kwd and kwd['age']:
                db.update('users', where='id = $id', age = kwd['age'], vars = locals())
            if 'degree' in kwd and kwd['degree']:
                db.update('users', where='id = $id', degree = kwd['degree'], vars = locals())
            if 'email' in kwd and kwd['email']:
                db.update('users', where='id=$id', email=kwd['email'], vars=locals())

            if 'password' in kwd and kwd['password']:
                pwdhash = hashlib.md5(kwd['password']).hexdigest()
                db.update('users', where='id=$id', password=pwdhash, vars=locals())

            if 'picture' in kwd and kwd['picture']:
                db.update('users', where='id=$id', picture=kwd['picture'], vars=locals())

            if 'description' in kwd and kwd['description']:
                db.update('users', where='id=$id', description=kwd['description'], vars=locals())
            
            return True
        except Exception, e:
            print e
            return False

    def login(self, username, password):
        '''登录验证'''
        pwdhash = hashlib.md5(password).hexdigest()
        users = db.select('users', what='id', where='name=$username AND password=$pwdhash', vars=locals())
        #users = db.where('users', name=username, password=pwdhash)
        if users:
            u = users[0]
            return u.id
        else:
            return 0

    def status(self, id):
        '''查询id对应的用户信息'''
        email = ''
        username = ''
        password_hash = ''
        picture = ''
        description = ''

        users = db.query('SELECT email, name, password, picture, description FROM users WHERE id=%d' % id)
        if users:
            u = users[0]
            email = u.email
            username = u.name
            password_hash = u.password
            picture = u.picture
            description = u.description

        return {'email': email, 'username': username, 'password_hash': password_hash,
                'picture': picture, 'description': description}

    def matched_id(self, **kwd):
        '''根据kwd指定的查询条件，搜索数据库'''
        users = db.select('users', what='id', where=web.db.sqlwhere(kwd, grouping='OR'))
        if users:
            # 目前只用于单条记录查询，因此只取第一个
            u = users[0]
            return u.id
        else:
            return 0

    def current_id(self):
        '''当前登录用户的id'''
        user_id = 0
        try:
            user_id = int(web.cookies().get('user_id'))
        except Exception, e:
            print e
        else:
            # 刷新cookie
            web.setcookie('user_id', str(user_id), settings.COOKIE_EXPIRES)
        finally:
            return user_id
    
    @staticmethod
    def fuction_2(part_name):
        users = db.query('''SELECT distinct user_id
                            FROM posts
                            WHERE posts.part = $part_name''',vars = locals())
        users = convert_db_dic(users)
        for i in range(len(users)):
            users[i]['post_number'] = User.post_number(users[i]['user_id'])
            users[i]['reply_number'] = User.reply_number(users[i]['user_id'])

        post_arrange =  sorted(users, key=lambda user:user['post_number'])
        reply_arrange =  sorted(users, key=lambda user:user['reply_number'])


        #users = users[0]
        return post_arrange, reply_arrange

    @staticmethod
    def post_number(user_id):
        #返回用户发帖总数
        number = db.query('''SELECT count(*)
                             FROM posts
                             WHERE posts.user_id = %d''' % user_id, vars = locals())
        number = convert_db_dic(number)
        return number[0]['count(*)']
    @staticmethod
    def reply_number(user_id):
        number = db.query('''SELECT count(*)
                             FROM comments
                             WHERE comments.user_id = %d''' % user_id, vars = locals())
        if number:
            return number[0]['count(*)']
        else:
            return 0

class Post:
    def new(self, title, content, user_id):
        if user_id:
            return db.insert('posts', title=title, content=content, user_id=user_id,click_count = 0, reply_count = 0, part = 'A')
        else:
            return 0
    @staticmethod
    def top_10_click_count():
        posts = db.query('''SELECT posts.id
                            FROM posts 
                            ORDER BY click_count DESC
                            LIMIT 10 ''')
        posts = convert_db_dic(posts)[0]
        return posts
    @staticmethod
    def top_10_reply_count():
        posts = db.query('''SELECT posts.id
                            FROM posts 
                            ORDER BY reply_count DESC
                            LIMIT 10 ''')
        posts = convert_db_dic(posts)[0]
        return posts

    def update(self, id, title, content):
        try:
            db.update('posts', where='id=$id', title=title, content=content, vars=locals())
            return True
        except Exception, e:
            print e
            return False
        
    def view(self, id):
        '''获取id对应的文章'''
        posts = db.query('''SELECT posts.id, title, content, click_count, posts.time, user_id, users.name AS username, users.picture AS user_face
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            WHERE posts.id = %d''' % id)
        if posts:
            posts = posts[0]
            click_count = posts.click_count + 1
            #print("___click__\n")
            #print(click_count)
            db.update('posts', where='id=$id', click_count = click_count, vars=locals())
            ## update click number
            return posts

        return None

    def ddel(self, id):
        try:
            db.delete('posts', where='id=$id', vars=locals())
            #db.query('DELETE FROM posts WHERE id=%d' % id)
        except Exception, e:
            print e

    def list(self, page):
        '''获取第page页的所有文章'''
        per_page = settings.POSTS_PER_PAGE

        # 获取从offset开始共per_page个post
        offset = (page - 1) * per_page
        posts = db.query('''SELECT posts.id, title, posts.time, user_id, click_count, users.name AS username
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            ORDER BY posts.id DESC
                            LIMIT %d OFFSET %d''' % (per_page, offset))
        page_posts = []
        for p in posts:
            comment = Comment(p.id)
            last = comment.last()
            last_time = last.time if last else p.time
            # and click count
            page_posts.append({'id': p.id, 'title': p.title, 'click_count':p.click_count,'userid': p.user_id, 'username': p.username, 'comment_count': comment.count(), 'last_time': last_time})

        # 计算总页数
        post_count = self.count()
        page_count = post_count / per_page
        if post_count % per_page > 0:
            page_count += 1

        return (page_posts, page_count)

    def digest_list(self, user_id):
        '''获取user_id对应作者的文章列表'''
        posts = db.query('''SELECT id, title, time FROM posts
                            WHERE user_id=%d
                            ORDER BY id DESC''' % user_id)
        return posts

    def count(self):
        '''获取文章总数'''
        return db.query("SELECT COUNT(*) AS count FROM posts")[0].count

    def query_hotness(self):
        for part in part_name:
            part_posts = db.query('''SELECT posts.time, posts.id, posts.user_id
                FROM posts
                WHERE posts.part=%d''' % part)
            for post in part_posts:
                last_comment = Comment(post[id])



class Comment:
    def __init__(self, post_id):
        '''一个Comment实例只对应一篇文章'''
        self.__parent_id = post_id

    def quote(self, comments):
        '''为每个评论获取父评论（即引用，只处理一级）'''
        comments_with_quote = []
        for c in comments:
            quote_content = ''
            quote_username = ''
            quote_user_id = 0
            if c.quote_id:
                quotes = db.query('''SELECT content, users.name AS username, user_id
                                       FROM comments JOIN users
                                       ON comments.user_id = users.id
                                       WHERE comments.id=%d''' % c.quote_id)
                if quotes:
                    q = quotes[0]
                    quote_content = q.content
                    quote_username = q.username
                    quote_user_id = q.user_id
            comments_with_quote.append({'id': c.id, 'content': c.content, 'user_id': c.user_id, 'username': c.username,
                                        'user_face': c.user_face, 'time': c.time, 'quote_content': quote_content,
                                        'quote_username': quote_username, 'quote_user_id': quote_user_id})
        return comments_with_quote

    def new(self, content, user_id, quote_id = -1):
        try:
            if quote_id == -1:
                return db.insert('comments', content=content, user_id=user_id, parent_id=self.__parent_id)
            # not quote_id !
            else:
                return db.insert('comments', content=content, user_id=user_id, parent_id=self.__parent_id, quote_id=quote_id)
        except Exception, e:
            print e
            return 0

    def ddel(self):
        try:
            #db.delete('comments', where='parent_id=$self.__parent_id', vars=locals())
            db.query('DELETE FROM comments WHERE parent_id=%d' % self.__parent_id)
        except Exception, e:
            print e

    def list(self):
        '''获取当前文章（创建Comment实例时指定了post_id）下面的所有评论'''
        comments = db.query('''SELECT comments.id, content, comments.time, users.name AS username, user_id, quote_id, users.picture AS user_face
                               FROM comments JOIN users
                               ON comments.user_id = users.id
                               WHERE comments.parent_id=%d
                               ORDER BY comments.id''' % self.__parent_id)
        return comments

    def last(self):
        '''获取当前文章下面的最新评论'''
        last_comments = db.query('''SELECT comments.id, content, comments.time, users.name AS username, user_id , users.picture AS user_face
                                    FROM comments JOIN users
                                    ON comments.user_id = users.id
                                    WHERE comments.id=(SELECT MAX(id) FROM comments WHERE parent_id=%d)''' % self.__parent_id)
        if last_comments:
            #print(last_comments[0]) #!! ATTENTION  This line will make a bug！！
            # After last_comments[0];  last_comments has been changed into last_comments[0]  Why?
            return last_comments[0]

        return None

    def count(self):
        '''获取当前文章下面的评论总数'''
        return db.query("SELECT COUNT(*) AS count FROM comments WHERE parent_id=%d" % self.__parent_id)[0].count

if __name__ == '__main__':
    post = Post().new('title', 10, 1)
    a = User().post_number(1)
    b = User().fuction_2('A')
    print(b)
    #print(a[0]['count(*)'])
    #comment = Comment(3).new(10, 1)
    #a = Comment(3).last()
    #b = Post.top_10_reply_count()
    #print(b[0])
    #print(a)
    #print(a[0]['username'])