from xml.dom.minidom import Document
import model
def writeInfoToXml(filename):
  $model.user[name]
  doc = Document()
  users = doc.createElement('Users')
  doc.appendChild(users)
  user = doc.createElement('User')
  users.appendChild(user)
  userName = doc.createElement('UserName')
  user.appendChild(userName)
  Name = doc.createTextNode([])
  userName.appendChild(Name)
  info = doc.createElement('Info')
  basicinfo = doc.createElement('BasicInfo')

  with open(filename, 'w') as f:
    f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
  return
if __name__ == '__main__':
  writeInfoToXml('./a.xml')