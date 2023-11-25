import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    # 파일 객체 선언
    f = open("../korean_name_data.json", 'w')
    
    f.write('{"pages":[')
    for i in range(1, 21):
        # requests 라이브러리를 활용한 HTML 페이지 요청
        # res 객체에 HTML 데이터를 저장하고, res.content로 데이터 추출 가능
        res = requests.get(f'https://www.namechart.kr/en/chart/2008?page={i}')
        
        # HTML 페이지 파싱
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 이름 데이터 검색
        name_data = soup.find(id='__NEXT_DATA__')
        
        # 데이터 추출하여 JSON 파일에 저장
        f.write(name_data.string)
        if i < 20:
            f.write(',\n')
    
    f.write(']}')
    f.close()