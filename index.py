from flask import Flask, redirect, url_for, render_template, request
from flask.json.tag import JSONTag
import json
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly
import plotly.express as px

app = Flask(__name__)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


db = firestore.client()

@app.route("/")
def dashnoard():


    db = firestore.client()
    emp_ref = db.collection('sale').order_by('date')
    docs = emp_ref.stream()

    # declare empty list
    df1 = []
    df2 = []
    df3 = []

    for doc in docs:
        #print('{} => {}'.format(doc.id, doc.to_dict()))
        
        prod_name_data = {k: v for k, v in doc.to_dict().items() if k.startswith('product_name')}
        df1.append(prod_name_data)
        #print(prod_name_data)
        
        date_data = {k: v for k, v in doc.to_dict().items() if k.startswith('date')}
        df2.append(date_data) 
        #date_list.append(date_data)

        revenue_data = {k: v for k, v in doc.to_dict().items() if k.startswith('revenue')}
        df3.append(revenue_data)
        #print(revenue_data)

    # First DataFrame
    df1 = pd.DataFrame(df1)
    # Second DataFrame
    df2 = pd.DataFrame(df2)
    # Third DataFrame
    df3 = pd.DataFrame(df3)

    # the default behaviour is join='outer'
    # inner join to join 3 dataframes
    merged = pd.concat([df1, df2], axis = 1, join = 'inner')
    merged.loc[:,'revenue'] = df3

    merged[['revenue']] = merged[['revenue']].apply(pd.to_numeric)
    merged[['date']] = merged[['date']].apply(pd.to_datetime)
    # df4 = pd.DataFrame(merged)

    # chart 1
    fd = px.data.medals_wide()
    fig1 = px.bar(merged,x='date' , y='revenue', color='product_name', title="Daily Sales") #if tak cantik pakai bar, tukar histogram
    fig1.update_layout(bargap=0.2)
    #fig1.show()

    # chart 2
    fig2 = px.line(merged, x="date", y="revenue", color="product_name", title="The visualisation of each Product Sales")
    fig2.update_traces(textposition="bottom right")
    #fig2.show()

    # chart 3
    fig3 = px.line(merged, x='date', y="revenue", facet_col="product_name", facet_col_wrap=2,
                facet_row_spacing=0.07, # default is 0.07 when facet_col_wrap is used
                facet_col_spacing=0.06, # default is 0.03
                height=600, width=800,
                title="Let's see the Product Sales visualisation seperately!")
    fig3.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig3.update_yaxes(showticklabels=True)
    fig3.update_layout(bargap=0.2)
    #fig3.show()

    # chart 4
    merged['date'] = pd.to_datetime(merged['date'])
    merged = merged.set_index('date') 
    df = merged['2013-01-01':'2013-06-30'].resample('M').sum()

    fig4=px.bar(df,title='Monthly sales for all products')
    #fig4.show()

    # the default behaviour is join='outer'
    # inner join to join 3 dataframes
    merged = pd.concat([df1, df2, df3], axis = 1, join = 'inner')
    merged[['revenue']] = merged[['revenue']].apply(pd.to_numeric)
    merged[['date']] = merged[['date']].apply(pd.to_datetime)

    print("Monthly Sales per Product")
    merged.groupby([pd.Grouper(key='date', freq='M'),'product_name']).agg({'revenue':sum})

    #figureList = [fig1, fig2, fig3, fig4]
    #figure 1
    graph1JSON = json.dumps(fig1, cls = plotly.utils.PlotlyJSONEncoder)
    #figure 2
    graph2JSON = json.dumps(fig2, cls = plotly.utils.PlotlyJSONEncoder)
    #figure 3
    graph3JSON = json.dumps(fig3, cls = plotly.utils.PlotlyJSONEncoder)
    #figure 4
    graph4JSON = json.dumps(fig4, cls = plotly.utils.PlotlyJSONEncoder)
    return render_template("new.html", title="Home",graph1JSON = graph1JSON, graph2JSON = graph2JSON, graph3JSON = graph3JSON, graph4JSON = graph4JSON)


if __name__ == "__main__":
    app.run(debug=True)