import requests
import pandas as pd

#API den verileri çekmek için HTTP GET isteği yapar
def get_data(market_code):
    url = f"https://www.bitexen.com/api/v1/order_book/{market_code}/"
    response = requests.get(url)
    if response.status_code!=200:
        raise Exception(f"API requests faild {response.status_code}")
    return response.json()['data']

#veri analizi yaparak hesaplamalar yapılır
def analyses_data(data,key):
    prices = [float(item[key]) for item in data]
    amount = [float(item['orders_total_amount']) for item in data] if 'orders_total_amount' in data[0] else [float(item['amount']) for item in data]
    
    return{
        'min_prices':min(prices),
        'max_prices':max(prices),
        'avg_prices':sum(prices)/len(prices),
        'total_volume':sum(amount),
    }
    
# istenilen verileri analiz ederek sonuçları dictionary olarak tutar
def analyses_order_book(data):
    buyers = data['buyers']
    sellers = data['sellers']
    transactions = data['last_transactions']
    
    return{
        'buyers' :analyses_data(buyers,"orders_price"),
        'sellers':analyses_data(sellers,"orders_price"),
        'transactions':analyses_data(transactions,"price")
    }
    
# veriler tek bir tabloda birleştirilerek excel'e kaydedilir 
def save_to_excel(filename,analyses,symbols):
    with pd.ExcelWriter(filename) as writer:
        for symbol,analysis in zip(symbols,analyses):
            
            buyers_pd = pd.DataFrame(analysis['buyers'],index=[0])
            sellers_pd = pd.DataFrame(analysis['sellers'],index=[0])
            transactions_pd = pd.DataFrame(analysis['transactions'],index=[0])
            
            concat_pd =pd.concat([buyers_pd.T,sellers_pd.T,transactions_pd.T], axis=1)  
            concat_pd.columns =['Buyers', 'Sellers', 'Last_Transactions']
            concat_pd.to_excel(writer,sheet_name=symbol)
    

# gerekli string bilgiler kullanılarak kod çalıştırılır
def run():
    filename='bitexen_order_book_analysis.xlsx'
    symbols=["TRY - BTCTRY","USDT - BTCUSDT"]
    market_codes =['BTCTRY','BTCUSDT']
    analyses=[]
    
    for market_code in market_codes:
        data = get_data(market_code)
        analysis = analyses_order_book(data)
        analyses.append(analysis)
    save_to_excel(filename,analyses,symbols)

if __name__=='__main__':
    run()