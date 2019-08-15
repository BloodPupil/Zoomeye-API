import pickle
import requests
import threading
import Queue
#------------------------------------------------------the follows should not be used directly-------------------------------------------------------------------#
class HostQueryData:
        __slots__ = ('content','app','ver','device','os','service','ip','cidr','hostname','port','city','country','asn')
        def __init__(self):
                self.content = ''
                self.app = ''
                self.ver = ''
                self.device = ''
                self.os = ''
                self.service = ''
                self.ip = ''
                self.cidr = ''
                self.hostname = ''
                self.port = ''
                self.city = ''
                self.country = ''
                self.asn = ''
                
        def show(self):
                dc = self.__dict__
                for i in dc:
                        print '%s:%s'%(i,dc[i] if dc[i] else 'Not Yet Set')
 
class WebQueryData:
        __slots__ = ('content','app','header','keywords','desc','title','ip','site','city','country')
        def __init__(self):
                self.content = ''
                self.app = ''
                self.header = ''
                self.keywords = ''
                self.desc = ''
                self.title = ''
                self.ip = ''
                self.site = ''
                self.city= ''
                self.country = ''
                
        def show(self):
                dc = self.__dict__
                for i in dc:
                        print '%s:%s'%(i,dc[i] if dc[i] else 'Not Yet Set')
                        
class HostFacetsData(object):
        def __init__(self):
                #True or False
                self.app = False
                self.device = False
                self.os = False
                self.service = False
                self.port = False
                self.city = False
                self.country = False
        
        def __setattr__(self,name,value):
                if not isinstance(value,bool):
                        print 'Value Type Error'
                        return
                else:
                        return object.__setattr__(self,name,value)
                
        def show(self):
                dc = self.__dict__
                for i in dc:
                        print '%s:%s'%(i,dc[i])
                       
class WebFacetsData(object):
        def __init__(self):
                #True or False
                self.webapp = False
                self.component = False
                self.framework = False
                self.frontend = False
                self.server = False
                self.waf = False
                self.os = False
                self.city= False
                self.country = False
                
        def __setattr__(self,name,value):
                if not isinstance(value,bool):
                        print 'Value Type Error'
                        return
                else:
                        return object.__setattr__(self,name,value)
                
        def show(self):
                dc = self.__dict__
                for i in dc:
                        print '%s:%s'%(i,dc[i])
                        
#------------------------------------------------------The class you should use---------------------------------------------------------#                     
class ZoomEye:
        def __init__(self,type,username,password,start_page = 1,end_page = 10,rate = 5):
                self.__type = type
                self.__start_page = start_page
                self.__end_page = end_page
                self.__rate = rate
                try:
                        response =  requests.post(url='https://api.zoomeye.org/user/login',data ='{"username": "%s","password": "%s"}'%(username,password))
                        if response.status_code != 200:
                                print "Get access_token failed:%s   reason:%s"%(response.status_code,response.reason)
                                print "Init faliled!"
                                return 
                        self.__access_token = response.json()['access_token']
                except Exception as e:
                        print e
                self.__en = parse_entity()
                self.__hostquerydata = HostQueryData()
                self.__hostfacetsdata = HostFacetsData()
                self.__webquerydata = WebQueryData()
                self.__webfacetsdata = WebFacetsData()
                if type == 'host':
                        self.query_data = self.__hostquerydata
                        self.facets_data = self.__hostfacetsdata
                elif type == 'web':
                        self.query_data = self.__webquerydata
                        self.facets_data = self.__webfacetsdata 
                else:
                        self.__type = None
                        print 'Please select right type!'
          
        def get_result(self):
                return self.__en
         
        def show(self,level = 'v'):
                self.__make_args()
                print 'Query type:%s'%self.__type
                print 'Query args:(as follows)'
                for i in self.__tmp_query_data:
                        print '                  %s'%i
                print 'Your access_token:%s'%self.__access_token
                print 'Pages from %s to %s'%(self.__start_page,self.__end_page)
                print 'Threads rate:%s'%self.__rate
                if self.__en.total == 0:
                        print 'Got result:There is nothing!'
                else:
                        print 'Got resutl:Total records:%s'%self.__en.total
                        if level == 'v':
                                print 'Got resutl:Matches Records:(as follows:)'
                                for i in self.__en.matches:
                                        i.show(3)
                                        print ''
                                if self.__en.facets:
                                        print 'Got resutl:Facets Records:(as follows:)'
                                        self.__en.facets.show(3)
                                
                                
                                
                                
                                
        def __make_args(self):
                self.__query_args = Queue.Queue()
                self.__tmp_query_data = []
                
                query_string = ''
                tmp_data = '' 
                query_data = self.query_data.__dict__
                for i in query_data:
                        if query_data[i]:
                                if i == 'content':
                                        tmp_data += '%s '%query_data[i]
                                        continue
                                tmp_data += '%s:%s '%(i,query_data[i])
                query_string = tmp_data[:-1]
               
                facets_string = ''
                tmp_data = ''
                facets_data = self.facets_data.__dict__
                for i in facets_data:
                        if facets_data[i]:
                                tmp_data += '%s,'%i
                facets_string=  tmp_data[:-1]     
                
                for i in range(self.__start_page,self.__end_page+1):
                        params = dict()
                        if query_string:
                                params['query'] = query_string
                        if facets_string:
                                params['facets'] = facets_string
                        params['page'] = i                     
                        self.__query_args.put(params)
                        self.__tmp_query_data.append(params)
          
        def __action(self):
                while not self.__query_args.empty():
                        headers = {"Authorization":"JWT "+self.__access_token}
                        try:
                                params=self.__query_args.get()
                                print "Querying:  "+ str(params)
                                r = requests.get(url='https://api.zoomeye.org/%s/search?'%self.__type ,
                                                 params=params,
                                                 headers = headers)
                                if r.status_code != 200:
                                        print 'Request Failed:%s      reason:%s'%(r.status_code,r.reason)
                                        return
                                self.__response.put(r.json())
                        except Exception as e:
                                print 'Exception:%s'%e
                                return
                        
        def query(self,payload = None):
                self.__response = Queue.Queue()
                self.__make_args()
                t_list = []
                if self.__rate == 0:
                        t = threading.Thread(target=self.__action)
                        t.start()
                        t_list.append(t)                        
                else:
                        for i in range((self.__end_page-self.__start_page)/self.__rate):
                                t = threading.Thread(target=self.__action)
                                t.start()
                                t_list.append(t)
                for i in t_list:
                        i.join()
                while not self.__response.empty():
                        self.__en.feed(self.__response.get())
        

#------------------------------------------------------the follows should not be used directly-------------------------------------------------------------------#
#parser
class tmp:
        def show(self,level = 0):
                show(self,level)

def parse(dict_data):
        et = tmp()
        if not dict_data:
                print 'Please feed something!'
                return et
        for i in dict_data:
                if isinstance(dict_data[i],dict):
                        setattr(et,i,parse(dict_data.get(i)))
                else:
                        setattr(et,i,dict_data.get(i))
        return et

#show
def show(ins,level = 0):
        if not  ins:
                print 'There is nothing!'
                return 
        tmp = ins.__dict__
        fm = '      '*level
        for i in tmp:
                if 'instance' in str(type(tmp[i])):
                        print '%s%s:'%(fm,i)
                        show(tmp[i],level+1)
                else:
                        print '%s%s:%s'%(fm,i,tmp[i])
                        
                        
class parse_entity:
        def __init__(self):
                self.matches = []
                self.total = 0
                self.facets = None
        
        def feed(self,data):
                if self.total == 0:
                        self.total = data.get('total')
                if not self.facets and data.get('facets'): 
                        self.facets = parse(data.get('facets'))
                if data.get('matches'):
                        for i in data.get('matches'):
                                self.matches.append(parse(i))