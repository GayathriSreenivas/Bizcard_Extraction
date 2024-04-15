
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector


sql_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="gayathri@123",
                database="business_card"
            )
sqlcursor = sql_connection.cursor()

create = '''CREATE TABLE IF NOT EXISTS bizcard(name varchar(225),
                                               designation varchar(225),
                                               company_name varchar(225),
                                               contact varchar(225),
                                               email varchar(225),
                                               website varchar(225),
                                               address varchar(255),
                                               pincode varchar(225),
                                               image VARBINARY(65535))'''

sqlcursor.execute(create)
sql_connection.commit()

def image_to_text(path):
    input_img = Image.open(path)

    # converting image to array format
    image_arr = np.array(input_img)

    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_arr, detail=0)

    return text, input_img


def extracted_text(texts):
    extracted = {"NAME": [], "DESIGNATION": [], "COMPANY_NAME": [], "CONTACT": [], "EMAIL": [], "WEBSITE": [],
                 "ADDRESS": [], "PINCODE": []}

    extracted["NAME"].append(texts[0])
    extracted["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extracted["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            extracted["EMAIL"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extracted["WEBSITE"].append(small)

        elif texts[i].isdigit():
            extracted["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):
            extracted["COMPANY_NAME"].append(texts[i])

        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extracted["ADDRESS"].append(remove_colon)

    for key, value in extracted.items():
        if len(value) > 0:
            concatenate = " ".join(value)
            extracted[key] = [concatenate]

        else:
            value = "NA"
            extracted[key] = [value]

    return extracted;

#STREAMLIT PART

st.set_page_config(layout = "wide")
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: linear-gradient(to bottom , #eafacd, #a7f516);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("BUSINESS CARD DATA EXTRACTION")

with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Upload & Modify", "Delete"])

if select == "Home":
    pass

elif select == "Upload & Modify":
    img = st.file_uploader("Upload the Image", type=["png", "jpg", "jpeg"])

    if img is not None:
        st.image(img, width=300)

        text_img, imgs = image_to_text(img)

        text = extracted_text(text_img)

        if text:
            st.success("TEXT EXTRACTED SUCCESSFULLY")

        df = pd.DataFrame(text)
        image_bytes = io.BytesIO()
        imgs.save(image_bytes, format="PNG")
        img_data = image_bytes.getvalue()

        data = {"IMAGE": [img_data]}

        df1 = pd.DataFrame(data)
        finaldf = pd.concat([df, df1], axis=1)

        st.table(finaldf)

        button = st.button("Save to DB",use_container_width= True)

        if button:
            insert = '''INSERT INTO bizcard(name , designation, company_name , contact , email , website , address , pincode , image)
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            values = [tuple(row) for row in finaldf.values]
            sqlcursor.executemany(insert,values)
            sql_connection.commit()
            st.success("DATA SAVED SUCCESSFULLY")
    method = st.radio("Select option", ["Read Data","Modify"])

    if method == "Read Data":
        sql_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="gayathri@123",
            database="business_card"
        )
        sqlcursor = sql_connection.cursor()
        select = "select * from bizcard;"

        sqlcursor.execute(select)
        table = sqlcursor.fetchall()
        sql_connection.commit()

        columns = ["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"]
        table_df = pd.DataFrame(table, columns=columns)

        st.dataframe(table_df)

    if method == "Modify":
        sql_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="gayathri@123",
            database="business_card"
        )
        sqlcursor = sql_connection.cursor()
        select = "select * from bizcard;"

        sqlcursor.execute(select)
        table = sqlcursor.fetchall()
        sql_connection.commit()

        table_df = pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))

        if len(table_df) != 0:
            col1,col2 = st.columns(2)
            with col1:
                options = ["None"] + list(table_df["NAME"])

                selected_name = st.selectbox("Select the name", options, index=0)

            if selected_name != "None":

                df_3 = table_df[table_df["NAME"] == selected_name]

                df_4 = df_3.copy()
                df_4["IMAGE"] = ""

                col1,col2 = st.columns(2)
                with col1:
                    name = st.text_input("Name",df_3["NAME"].unique()[0])
                    designation = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
                    company = st.text_input("Company_name", df_3["COMPANY_NAME"].unique()[0])
                    contact = st.text_input("Contact",df_3["CONTACT"].unique()[0])
                    email = st.text_input("Email", df_3["EMAIL"].unique()[0])

                    df_4["NAME"] = name
                    df_4["DESIGNATION"] = designation
                    df_4["COMPANY_NAME"] = company
                    df_4["CONTACT"] = contact
                    df_4["EMAIL"] = email

                with col2:
                    website = st.text_input("Website", df_3["WEBSITE"].unique()[0])
                    address = st.text_input("Address", df_3["ADDRESS"].unique()[0])
                    pincode = st.text_input("Pincode", df_3["PINCODE"].unique()[0])
                    image = st.text_input("Image", df_3["IMAGE"].unique()[0])

                    df_4["WEBSITE"] = website
                    df_4["ADDRESS"] = address
                    df_4["PINCODE"] = pincode
                    df_4["IMAGE"] = image

                col1,col2 = st.columns(2)
                with col1:
                    button_3 = st.button("Modify", use_container_width=True)

                if button_3:
                    sql_connection = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="gayathri@123",
                        database="business_card"
                    )
                    sqlcursor = sql_connection.cursor()

                    update = '''UPDATE bizcard SET name=%s, designation=%s, company_name=%s, 
                                contact=%s, email=%s, website=%s, address=%s, pincode=%s, image=%s 
                                WHERE name=%s'''

                    name_to_update = df_3["NAME"].unique()[0]
                    updated_values = df_4.iloc[0].values.tolist()
                    updated_values.append(name_to_update)

                    sqlcursor.execute(update, updated_values)
                    sql_connection.commit()

                    st.success("MODIFICATION DONE SUCCESSFULLY")
                    st.table(df_4)

elif select == "Delete":
    sql_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gayathri@123",
        database="business_card"
    )
    sqlcursor = sql_connection.cursor()

    # col1, col2 = st.columns(2)
    # with col1:
    select_query = "SELECT NAME FROM bizcard;"
    sqlcursor.execute(select_query)
    table = sqlcursor.fetchall()
    sql_connection.commit()

    names = []

    for i in table:
        names.append(i[0])

    select_name = st.selectbox("Select the name to delete",names)

    # with col2:
    remove = st.button("Delete", use_container_width=True)

    if remove:
        sqlcursor.execute(f"DELETE FROM bizcard where name = '{select_name}'")
        sql_connection.commit()

        st.warning("DELETED")