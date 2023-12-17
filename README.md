# get3D_result_refine_process
get3D(3D 생성모델) 의 결과물을 개선시키는 프로세스

준비해야할 프로그램
1. blender 3.6.4 c드라이브에 설치
2. pip numpy install


개선 프로세스 수행 과정
1. refine 디렉토리의 improve_one_obj.py 스크립트를 실행
2. 파일 선택창이 켜지면, 개선을 원하는 obj파일 선택
   (obj파일, 텍스처(png)파일, mtl파일이 동일한 디렉토리에 위치해야함)
4. 개선프로세스 실행이 종료되면 refine 디렉토리의 output 디렉토리에 결과물 생성

*여러개의 obj파일을 한번에 개선시키고 싶다면 improve_in_directory.py를 실행시키고, 
개선을 원하는 obj파일들이 들어있는 디렉토리를 선택하면 된다.

get3D의 예시 파일은 아래의 구글드라이브 링크에서 받아볼 수 있음.
https://drive.google.com/file/d/11K1QsfyjH6U5mEIIWzR3_lND2Iymh-1n/view?usp=drive_link
