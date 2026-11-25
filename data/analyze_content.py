import json,re
from collections import defaultdict,Counter
B=[json.load(open(f))['data']['alexandria'] for f in ('batch1.json','batch2.json','batch3.json')]
items={}
REL=re.compile(r'휘낭|피낭|financier|whinan|구움과자|마들렌|답례품|디저트|쿠키|베이킹|baking|빵|선물|gift|dessert|bak',re.I)
OFF=re.compile(r'danganronpa|단간론파|메이크업|makeup|괴담|양갈비|생선|명란|무생채|반찬|곶감 판매|치킨|캘리그라피|키리모찌|가래떡|붕어빵|자가리코|NewJeans|빼빼로 뽀뽀|이경규|link nhạc|Yum$|unique dessert|whipped cream|무수단|돈케이크|생일선물로 주려|꿀 2kg|사탕 #젤리|피에로그루망|각과자|아몬드 조각|헤네치아|메이지|초코스쿱|두바이 초코쿠키 선물주기|만두 찔|Chuseok|Coupang|IU|A gift under|셀럽도|어른선물|Gift Expert|survival|Holiday Gifts|Kurly|한양대|부산맛집|韩国|맛집 모음$',re.I)
def add(src,key,title,views,likes=None,shares=None,saves=None,comments=None,date=None,query=None):
    if not title or not views: return
    if not REL.search(title) or OFF.search(title): return
    k=key or title
    if k in items: return
    items[k]=dict(src=src,title=title.replace('\n',' '),views=int(views),likes=likes,shares=shares,saves=saves,comments=comments,date=date,query=query)
for A in B:
    for a in A:
        d=a.get('data') or {}; cap=a.get('capability'); q=(a.get('records') and None)
        if cap=='youtube/search':
            for v in (d.get('videos') or [])+(d.get('shorts') or []):
                add('YouTube',v.get('id') or v.get('url'),v.get('title'),v.get('viewCountInt'),date=v.get('publishedTimeText'))
        elif cap=='tiktok/search-videos':
            for x in d.get('search_item_list') or []:
                s=x.get('statistics') or {}
                add('TikTok',x.get('aweme_id'),x.get('desc'),s.get('play_count'),s.get('digg_count'),s.get('share_count'),s.get('collect_count'),s.get('comment_count'),(x.get('create_time_utc') or '')[:10])
        elif cap=='instagram/search-reels':
            for x in d.get('reels') or []:
                add('Instagram',x.get('shortcode'),x.get('caption'),x.get('video_play_count') or x.get('video_view_count'),x.get('like_count'),None,None,x.get('comment_count'),str(x.get('taken_at'))[:10])
L=list(items.values())
CATS=[('선물·답례품·포장',r'선물|답례|포장|세트|gift|빼빼로|명절|설날|화이트데이|발렌타인|생신|새학기|선생님'),
      ('식감·정보',r'겉바속촉|빠작|쫀득|바삭|이유|차이|비밀|버터 테스트|맛있게 먹는 법|드세요|never buy|Maldon|정석|shocked|사먹|못 만드는'),
      ('맛집·매장 탐방',r'맛집|오픈런|리뷰|투어|빵지순례|방문|성지|줄서|종결|털어|택배|팝업|명동|성수|대전|정동|가볼만|구매처|후기|Gold Standard|brick|best-selling|iconic'),
      ('브랜드 신제품·한정',r'출시|신메뉴|뚜레쥬르|한정|런칭|오픈합니다|두쫀|두바이'),
      ('먹방·ASMR',r'먹방|asmr|mukbang|먹빵|eating|咀嚼'),
      ('사장·창업 브이로그',r'사장|창업|브이로그|vlog|대량|주문받|카페 사장|세트 주문'),
      
      ('레시피·홈베이킹',r'레시피|만들기|만들어|홈베이킹|반죽|recipe|making|homebak|baking|구워|굽')]
def cat(t):
    for n,p in CATS:
        if re.search(p,t,re.I): return n
    return '기타'
for x in L: x['cat']=cat(x['title'])
agg=defaultdict(lambda:dict(n=0,views=0,tt_plays=0,tt_likes=0,tt_shares=0,tt_saves=0,tt_n=0))
for x in L:
    g=agg[x['cat']]; g['n']+=1; g['views']+=x['views']
    if x['src']=='TikTok' and x['views']>0:
        g['tt_n']+=1; g['tt_plays']+=x['views']; g['tt_likes']+=x['likes'] or 0; g['tt_shares']+=x['shares'] or 0; g['tt_saves']+=x['saves'] or 0
tot=sum(x['views'] for x in L)
print('total items',len(L),'total views',tot, Counter(x['src'] for x in L))
res=[]
for c,g in sorted(agg.items(),key=lambda kv:-kv[1]['views']):
    r=dict(cat=c,n=g['n'],views=g['views'],share=round(100*g['views']/tot,1),avg=round(g['views']/g['n']),
           tt_n=g['tt_n'],like_rate=round(100*g['tt_likes']/g['tt_plays'],2) if g['tt_plays'] else None,
           save_rate=round(100*g['tt_saves']/g['tt_plays'],2) if g['tt_plays'] else None,
           share_rate=round(100*g['tt_shares']/g['tt_plays'],2) if g['tt_plays'] else None)
    res.append(r); print(r)
# keyword frequency weighted by views
KW={'겉바속촉/바삭/빠작':r'겉바속촉|바삭|빠작|빠삭|콰작|까쟉','쫀득/촉촉/묵직':r'쫀득|쫀쫀|촉촉|묵직|쫀덕','버터/태운버터':r'버터|butter','솔티카라멜/소금':r'솔티|소금|salt|말돈|Maldon','초코':r'초코|choco|발로나','두바이/두쫀':r'두바이|두쫀','무화과/크림치즈':r'무화과|크림치즈','얼그레이·말차·흑임자':r'얼그레이|말차|흑임자|인절미|쑥','레시피':r'레시피|recipe','선물/답례':r'선물|답례|gift','맛집/오픈런':r'맛집|오픈런|줄서','다이소/쉬운':r'다이소|쉬운|초간단|간단','한 반죽 여러 맛':r'한 가지 반죽|한가지 반죽|1가지반죽|한 반죽|가지맛|가지 맛|종류별|12종|9종|4종|6가지|9가지'}
kw=[]
for k,p in KW.items():
    m=[x for x in L if re.search(p,x['title'],re.I)]
    kw.append(dict(kw=k,n=len(m),views=sum(x['views'] for x in m)))
kw.sort(key=lambda r:-r['views']); print(kw)
top=sorted(L,key=lambda x:-x['views'])[:15]
for x in top: print(x['views'],x['src'],x['cat'],x['title'][:60])
json.dump(dict(total=len(L),total_views=tot,src=Counter(x['src'] for x in L),cats=res,kw=kw,top=top),open('agg.json','w'),ensure_ascii=False,indent=1)
