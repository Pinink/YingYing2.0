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
def init_bbs():
    db.insert('parts',part_name = 'A',part_text = 'I am Part A')
    db.insert('parts',part_name = 'B',part_text = 'I am Part B')
    db.insert('parts',part_name = 'C',part_text = 'I am Part C')
def task():
    Search1 = Post.function_1_1()
    Search12 = Post.function_1_2()
    Search_1 = [Search1, Search12]
    Search_2 = {}
    Search_2['A'] = User.function_2('A')
    #Search_2['A'][0] 为按post_number排序 
    #Search_2['B'][1] 为按reply_number 排序
    Search_2['B'] = User.function_2('B')
    Search_2['C'] = User.function_2('C')
    Search_4 = {}
    Search_4['A'] = Post.function_4_1('A')
    Search_4['B'] =Post.function_4_1('B')
    Search_4['C'] =Post.function_4_1('C')
    Search3  = Post.query_hotness()
    #Search3[0]['A'] 是A版热度帖子
    #Search3[1]['A'] 是A版热度用户
    Search5 = Post.more_active('A','B')
    #Search5是user信息的一个list
    return [Search_1,Search_2,Search3,Search_4,Search5]

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
class Part:
    def __init__(self,name):
        self.name = name
    def status(self):
        part = db.query('''SELECT * 
                           FROM parts
                           WHERE parts.name = $name''',var = locals())
        part = convert_db_dic(part)
        return part[0]
class User:
    def new(self, info):
        print("in User\n")
        print(info)
        pwdhash = hashlib.md5(info['password']).hexdigest()
        print("are you here _______")
        return db.insert('users', email=info['email'], name=info['username'], password=pwdhash, nickname = info['nickname'], birthday = info['birthday'],
                         gender = info['gender'], age = info['age'], degree = info['degree'], picture='/static/img/user_normal.jpg', description='',)
    def user_for_admin(self):
        users = db.query('''SELECT id, nickname
                            FROM users''')
        users = convert_db_dic(users)
        return users
    @staticmethod
    def user_info_for_output():
        pass
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
    def ddel(self, id):
        try:
            db.delete('users', where='id=$id', vars=locals())
            #db.query('DELETE FROM posts WHERE id=%d' % id)
        except Exception, e:
            print e
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
        email = ''
        username = ''
        password_hash = ''
        picture = ''
        description = ''
        degree = ''
        users = db.query('SELECT email, name as username, password, picture, description,degree FROM users WHERE id=%d' % id)
        users = convert_db_dic(users)
        '''if users:
            u = users[0]
            email = u.email
            username = u.name
            password_hash = u.password
            picture = u.picture
            description = u.description
            degree = u.degree
        return {'email': email, 'username': username, 'password_hash': password_hash,
                'picture': picture, 'description': description,'degree':degree}'''
        return users[0]
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
    def function_2(part_name):
        users = db.query('''SELECT distinct user_id, nickname ,gender, age
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            WHERE posts.part = $part_name''',vars = locals())
        users = convert_db_dic(users)
        if users == None:
            return None
        for i in range(len(users)):
            users[i]['post_number'] = User.post_number(users[i]['user_id'])
            users[i]['reply_number'] = User.reply_number(users[i]['user_id'])

        post_arrange =  sorted(users, key=lambda user:user['post_number'])
        reply_arrange =  sorted(users, key=lambda user:user['reply_number'])
        #users = users[0]
        return [post_arrange, reply_arrange]
    @staticmethod
    def function_4_2(part_name):
        pass
    @staticmethod
    def function_5():
        users = db.query('''
                    SELECT users.id, nickname
                    FROM users''')
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
    def new(self, title, content, part,user_id):
        if user_id:
            return db.insert('posts', title=title, content=content, user_id=user_id,click_count = 0, reply_count = 0, part = part)
        else:
            return 0
    @staticmethod
    def function_1_1(page = 1):
        posts = db.query('''SELECT posts.id, title, posts.time, user_id, click_count, users.name AS username
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            ORDER BY click_count DESC
                            LIMIT 10''')
        page_posts = []
        for p in posts:
            comment = Comment(p.id)
            last = comment.last()
            last_time = last.time if last else p.time
            # and click count
            page_posts.append({'id': p.id, 'title': p.title, 'click_count':p.click_count,'userid': p.user_id, 'username': p.username, 'comment_count': comment.count(), 'last_time': last_time})

        return page_posts
    @staticmethod
    def function_1_2(page = 1):

        posts = db.query('''SELECT posts.id, title, posts.time, user_id, click_count, users.name AS username
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            ORDER BY (SELECT COUNT(*) AS count FROM comments WHERE parent_id = posts.id) DESC
                            LIMIT 10''')
        page_posts = []
        for p in posts:
            comment = Comment(p.id)
            last = comment.last()
            last_time = last.time if last else p.time
            # and click count
            page_posts.append({'id': p.id, 'title': p.title, 'click_count':p.click_count,'userid': p.user_id, 'username': p.username, 'comment_count': comment.count(), 'last_time': last_time})
            
        return page_posts
    
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

    @staticmethod
    def function_4_1(part_name):
        posts = db.query('''
                    SELECT posts.id, title, posts.time, user_id, click_count, users.name AS username
                    FROM posts JOIN users
                    ON posts.user_id = users.id
                    WHERE posts.click_count >= (
                        SELECT avg(click_count)
                        FROM posts
                        WHERE posts.part = $part_name) AND posts.part = $part_name''', vars = locals())
        page_posts = []
        for p in posts:
            comment = Comment(p.id)
            last = comment.last()
            last_time = last.time if last else p.time
            # and click count
            page_posts.append({'id': p.id, 'title': p.title, 'click_count':p.click_count,'userid': p.user_id, 'username': p.username, 'comment_count': comment.count(), 'last_time': last_time})
        return page_posts

    def list_differentpart(self, page,part_name):
        '''获取第page页的所有文章'''
        per_page = settings.POSTS_PER_PAGE

        # 获取从offset开始共per_page个post
        offset = (page - 1) * per_page
        posts = db.query('''SELECT posts.id, title, posts.time, user_id, click_count, users.name AS username
                            FROM posts JOIN users
                            ON posts.user_id = users.id
                            WHERE posts.part = $part_name
                            ORDER BY posts.id DESC
                            LIMIT $per_page OFFSET $offset''', vars = locals())
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

    @staticmethod
    def query_hotness():
        hot_post = {}
        hot_post_reply_user = {}
        for part in ['A','B','C']:
            part_posts = db.query('''SELECT posts.time, posts.id, posts.user_id, posts.title, posts.part, posts.content
                FROM posts
                WHERE posts.part=$part''', vars = locals())
            part_posts = convert_db_dic(part_posts)
            part_hottness = datetime.timedelta.max
            if not part_posts:
                continue
            for post in part_posts:
                # print(post)
                last_comment = Comment(int(post['id'])).last()
                if not last_comment:
                    continue
                hotness = last_comment['time'] - post['time']
                if hotness < part_hottness:
                    part_hottness = hotness
                    hot_post[part] = post
        for post in hot_post.values():
            reply_user = db.query('''SELECT DISTINCT comments.user_id
                FROM comments
                WHERE comments.parent_id=%ld'''% post['id'])
            reply_user = convert_db_dic(reply_user)
            hot_post_reply_user[post['part']] = reply_user
        return hot_post, hot_post_reply_user
        # return instance 

    @staticmethod
    def more_active(partA, partB):
        active_users = []
        users = convert_db_dic(db.query('''SELECT users.id, users.name, users.nickname
            FROM users'''))
        for user in users:
            tmp_id = user['id']
            numA = convert_db_dic(db.query('''SELECT COUNT(*) from posts where posts.user_id=%d AND posts.part=$partA'''%tmp_id, vars = locals()))
            numA = numA[0]['COUNT(*)']

            numB = convert_db_dic(db.query('''SELECT COUNT(*) from posts where posts.user_id=%d AND posts.part=$partB'''%tmp_id, vars = locals()))
            numB = numB[0]['COUNT(*)']
            if numA > numB:
                active_users.append(user)
        return active_users



class Comment:
    def __init__(self, post_id):
        '''一个Comment实例只对应一篇文章'''
        self.__parent_id = post_id
    def curlayer(self):
        layer = db.query('''SELECT layer
                    FROM comments
                    WHERE comments.id=(SELECT MAX(id) FROM comments WHERE parent_id=%d)''' % self.__parent_id)
        if layer:   
            return layer[0]['layer']
        else :
            return 0
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
            if c.layer == None:
                c.layer = 0
            comments_with_quote.append({'id': c.id, 'content': c.content, 'user_id': c.user_id, 'username': c.username,
                                        'user_face': c.user_face, 'time': c.time, 'quote_content': quote_content,
                                        'quote_username': quote_username, 'quote_user_id': quote_user_id,'layer':c.layer})
        return comments_with_quote

    def new(self, content, user_id, layer,quote_id = -1):
        try:
            if quote_id == '0':
                #print("are you heare?")
                return db.insert('comments', content=content, user_id=user_id, parent_id=self.__parent_id, layer = layer, like_count = 0)
            # not quote_id !
            else:
                return db.insert('comments', content=content, user_id=user_id, parent_id=self.__parent_id, quote_id=quote_id,layer = layer,like_count = 0)
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
        comments = db.query('''SELECT comments.id, content, comments.time, users.name AS username, user_id, quote_id, users.picture AS user_face, comments.layer
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

#if __name__ == '__main__':
    #post = Post().new('title', 10, 1)
    #a = User().post_number(1)
    #b = User().fuction_2('A')
    #print()
    #print(Post.function_4('A'))
    #print(a[0]['count(*)'])
    #comment = Comment(3).new(10, 1)
    #a = Comment(3).last()
    #b = Post.top_10_reply_count()
    #print(b[0])
    #print(a)
    #print(a[0]['username'])