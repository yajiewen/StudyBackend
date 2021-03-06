from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from account import models as amodels
from verify import models
import os
# Create your views here.

#配置nginx域名(部署的时候要改)
#nginxurl = 'http://124.70.87.28/'
nginxurl = 'http://47.242.184.92/'
#vimnginxurl = 'http://127.0.0.1/'
apply_review = 0
"""
------实名审核功能------
请求类型post
上传文件名:img1,img2
参数: cookies,uemail
api:https://127.0.0.1:8081/verify/iverify/
返回内容:
{
    'is_login':'yes',
    'is_upload':'yes'
}
"""
def identity_verify(request):
    if request.method == 'POST':
        #获取图片
        img1 = request.FILES.get('img1')
        img2 = request.FILES.get('img2')
        is_login = request.COOKIES.get('is_login') #获取登录状态
        usr_email = request.POST.get('uemail') #获取用户邮箱
        prefix = usr_email.split('@')[0] #获取前缀用于文件命名

        img1file = img1.read()
        img2file = img2.read()
        response_data = {
            'is_login':'no',
            'is_upload':'no'
        }
        if is_login and usr_email:
            response_data['is_login'] ='yes'
            if amodels.Table.objects.filter(usr_email=usr_email).exists():
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
                iverify_folder_path = os.path.join(os.path.join(base_path,'Imgfolder'),'Identity')
                if not os.path.exists(iverify_folder_path): #文件夹不存在则创建
                    os.makedirs(iverify_folder_path)
                    print(iverify_folder_path)
                
                #设置图片名字(同一个用户的身份证照片名字永远是同一个)
                img1name = prefix+'idenimg1.jpg'
                img2name = prefix+'idenimg2.jpg'
                #创建文件存储路径
                img1file_path = os.path.join(iverify_folder_path,img1name)  #文件名字格式prefix+idenimg1.jpg
                img2file_path = os.path.join(iverify_folder_path,img2name)
                #写入文件(因为名字相同,所以之前的图片会被覆盖)
                with open(img1file_path,'wb') as imgobj:
                    imgobj.write(img1file)
                
                with open(img2file_path,'wb') as imgobj:
                    imgobj.write(img2file)

                #配置imgurl
                img1url = nginxurl+'Identity/'+img1name
                img2url = nginxurl+'Identity/'+img2name
                
                #未上传则创建认证信息
                tab_objf = models.Table.objects.filter(usr_email=usr_email)
                if not tab_objf.exists():#未上传则创建认证信息
                    models.Table.objects.create(usr_email=usr_email,
                    usr_identity_imgurl1=img1url,
                    usr_identity_imgurl2= img2url,
                    usr_identity_imgpath1= img1file_path,
                    usr_identity_imgpath2= img2file_path,
                    usr_identity_status= apply_review,)
                else:
                    tab_objf.filter(usr_email=usr_email).update(
                        usr_identity_imgurl1=img1url,
                        usr_identity_imgurl2= img2url,
                        usr_identity_imgpath1= img1file_path,
                        usr_identity_imgpath2= img2file_path,
                        usr_identity_status= apply_review,)

                response_data['is_upload']= 'yes'
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)
"""
------学籍审核功能------
请求类型post
上传文件名:img1,img2
参数: cookies,uemail
api:https://127.0.0.1:8081/verify/sverify/
返回内容:
{
    'is_login':'yes',
    'is_upload':'yes'
}
"""
def student_verify(request):
    if request.method == 'POST':
        #获取图片
        img1 = request.FILES.get('img1')
        img2 = request.FILES.get('img2')
        is_login = request.COOKIES.get('is_login') #获取登录状态
        usr_email = request.POST.get('uemail') #获取用户邮箱
        prefix = usr_email.split('@')[0] #获取前缀用于文件命名

        img1file = img1.read()
        img2file = img2.read()

        response_data = {
            'is_login':'no',
            'is_upload':'no'
        }
        if is_login and usr_email:
            response_data['is_login'] ='yes'
            if amodels.Table.objects.filter(usr_email=usr_email).exists():
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
                sverify_folder_path = os.path.join(os.path.join(base_path,'Imgfolder'),'Studentstatus')
                if not os.path.exists(sverify_folder_path): #文件夹不存在则创建
                    os.makedirs(sverify_folder_path)
                    print(sverify_folder_path)
                #设置图片名字(同一个用户的身份证照片名字永远是同一个)
                img1name = prefix+'stuimg1.jpg'
                img2name = prefix+'stuimg2.jpg'
                #创建文件存储路径
                img1file_path = os.path.join(sverify_folder_path,img1name)
                img2file_path = os.path.join(sverify_folder_path,img2name)
                #写入文件(因为名字相同,所以之前的图片会被覆盖)
                with open(img1file_path,'wb') as imgobj:
                    imgobj.write(img1file)
                
                with open(img2file_path,'wb') as imgobj:
                    imgobj.write(img2file)

                #创建imgurl
                img1url = nginxurl+'Studentstatus/' + img1name
                img2url = nginxurl+'Studentstatus/' + img2name
                
                #未上传则创建认证信息
                tab_objf = models.Table.objects.filter(usr_email=usr_email)
                if not tab_objf.exists():#未上传则创建认证信息
                    models.Table.objects.create(usr_email=usr_email,
                    usr_student_imgurl1=img1url,
                    usr_student_imgurl2= img2url,
                    usr_student_imgpath1=img1file_path,
                    usr_student_imgpath2=img2file_path,
                    usr_student_status= apply_review,)
                else: #已存在则更新认证信息
                    tab_objf.filter(usr_email=usr_email).update(
                        usr_student_imgurl1=img1url,
                        usr_student_imgurl2= img2url,
                        usr_student_imgpath1=img1file_path,
                        usr_student_imgpath2=img2file_path,
                        usr_student_status= apply_review,)

                response_data['is_upload']= 'yes'
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data)
        else:
            return JsonResponse(response_data)
    else:
        return HttpResponse('bad request',status=500)