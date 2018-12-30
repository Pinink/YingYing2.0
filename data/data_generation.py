import random
import datetime
def users_generation():
	namefile = 'name.txt'
	name = []
	with open(namefile,'r') as f:
		fi = f.read()
		fi = fi.replace('\n', '')
		a = fi.split(' ')
		for i in a:
			if i and i[0] not in '0123456789':
				name.append(i)
	f.close()

	name_prefix = ['Angry ', 'Active ', 'Kind ', 'Handsome ', 'Sexy ', 'Honest ']
	birthday = datetime.datetime.now()
	gender_set = ['male', 'female']
	email_suffix = '@hotmail.com'
	degree = ['user', 'monitor', 'admin']
	password = '123456'
	picture = '/static/img/user_normal.jpg'

	cnt = 61
	for n in name:
		prefix_rand = random.randint(0, 5)
		gender_rand = random.randint(0, 1)

		nickname = name_prefix[prefix_rand] + n
		email = n + email_suffix
		age = 0
		# password = str(int((0.5 + random.random()) * 1e8))
		password = int((0.5 + random.random()) * 1e8)
		description = 'None'
		gender = gender_set[gender_rand]
		print(cnt, n, nickname, birthday, gender, age, email, degree[0],
		password, picture, description, datetime.datetime.now(), sep = ',', end = '\n') 
		cnt += 1

def corpus_preperation():
	corpus_file = './corpus.txt'
	with open(corpus_file, 'r') as f:
		corpus = f.read()
		corpus = corpus.replace('\n', ' ')
		corpus = ' '.join(corpus.split())
		sent = corpus.split('.')
		return sent

sent = corpus_preperation()	
def cont_generation():
	corpus_len = len(sent) - 10
	start = random.randint(0, corpus_len)
	post_len = random.randint(2, 10)
	tmp = sent[start: start + post_len]
	content = ''
	for s in tmp:
		content += s + '.'
	title = sent[random.randint(0, corpus_len)]
	return title, content

def posts_generation():
	part_name = ['A', 'B', 'C']
	cnt = 1
	for i in range(60):
		title, content = cont_generation()
		print(cnt, 'A', title, content, datetime.datetime.now(), 0, 0, i, sep = '=', end = '\n')
		cnt += 1
		title, content = cont_generation()
		print(cnt, 'B', title, content, datetime.datetime.now(), 0, 0, i, sep = '=', end = '\n')
		cnt += 1
		title, content = cont_generation()
		print(cnt, 'C', title, content, datetime.datetime.now(), 0, 0, i, sep = '=', end = '\n')
		cnt += 1

		num = random.randint(1, 5)
		for index in range(num):
			title, content = cont_generation()
			part_rand = random.randint(0, 2)
			print(cnt, part_name[part_rand], title, content, datetime.datetime.now(), 0, 0, i, sep = '=', end = '\n')
			cnt += 1

num_posts = 375
def comments_generation():
	cnt = 1
	for i in range(num_posts):
		num = random.randint(5, 100)
		for index in range(num):
			title, content = cont_generation()
			user_rand = random.randint(0, 60)
			print(cnt, content, datetime.datetime.now(), user_rand, title, 0, i, sep = '=', end = '\n')
			cnt += 1

if __name__ == '__main__':
	comments_generation()