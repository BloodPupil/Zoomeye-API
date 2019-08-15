import ZoomEye_API as ze
zm = ze.ZoomEye(type = 'web', username='Your Email', password ='Your password',start_page=1,end_page=100,rate=1) # rate page numbers/rate = thread number
zm.query_data.site = 'baidu.com' #target site
zm.query() 
zm.show()
