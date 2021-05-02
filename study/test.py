from django.shortcuts import render,HttpResponse
from django.http import JsonResponse

def imgtest(request):
    files = request.FILES.get('files')  #files 相当于已经打开了的二进制文件
    name=files.name
    files = files.read()
    response_data = {
        'is_login':'no',
        'is_add_order':'no',
        'order_token':''
                }
   
    with open(name,'wb') as f:
            f.write(files)


    print('wenjianyibaocun')
    return JsonResponse(response_data)

        