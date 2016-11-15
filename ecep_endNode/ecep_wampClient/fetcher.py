import urllib
import urllib2
import json
import os
ip = "localhost"#"ec2-52-32-10-8.us-west-2.compute.amazonaws.com"
port = 8070
route = '/download'
file_root_path = '/home/abhi/'

def get_file(**kwargs):
    key = ['username', 'containerName', 'filename']
    print kwargs
    for param in key:
        if param not in kwargs:
            raise ValueError("Missing %s" % param)

    url = 'http://' + ip + ':' + str(port) + route
    print url

    data = json.dumps(kwargs)
    headers = {'Content-Type': 'application/json'}
    try:
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        file_path = file_root_path + kwargs['username']+'_'+kwargs['conatinerName']+'/' +kwargs['filename']

        if not os.path.exists(file_root_path + kwargs['username']+'_'+kwargs['conatinerName']):
            os.makedirs(file_root_path + kwargs['username']+'_'+kwargs['conatinerName'])

        print(file_path)
        with open(file_path, 'wb') as output:
            while True:
                chunk = response.read(2048)
                if not chunk:
                    break
                output.write(chunk)
                print "downloading"
                output.flush()
        return file_path
    except Exception, e:
            print(e)

if __name__  == "__main__":

    data = {'username':'chinmayi','containerName':'app','filename':'test.mp3'}
    get_file(**data)


