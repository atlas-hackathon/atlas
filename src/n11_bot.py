#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib.request
import html
import time
import sys
import os
import emoji

TAG_RE = re.compile(r'<[^>]+>')

#Gelen html verisi içinden tagları tamamen temizliyor
def remove_tags(text):
    return TAG_RE.sub('', text)
#Müşterinin seçtiği emojiye göre gerekli puanlamayı yapmamızı sağlıyor
def icon_val(icon_str):
    if icon_str.find("iconPosSmly")!=-1:
        return 1
    if icon_str.find("iconNegSmly")!=-1:
        return -1

    return 0
#Siteye Http isteğinde bulunduğumuz fonksiyon
def httpistek(url, delay_time):
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
        request = urllib.request.Request(url, headers={'User-Agent': user_agent})

        response = urllib.request.urlopen(request)
        html = response.read()
        #Güvenlik duvarına yakalanmamak için her response dönüşü bekliyoruz
        time.sleep(delay_time)
        response.close()
        return html
    except:
        #Engellenme durumunda engelin kalkmasını bekliyoruz
        print(sys.exc_info()[1])
        if str(sys.exc_info()[1]).find("429") != -1:
            time.sleep(120)
            return 0
        return -1

def veri_temizle(veri):
    veri = re.sub(r'[.]{4,}', ' ... ', veri)
    veri = re.sub(r'^[.]+', '', veri)
    veri = re.sub(r'xa0', '', veri)
    veri = re.sub(r'[^\w,.:;\s]', '', veri)
    veri=veri.replace("\n", "").lstrip().rstrip()
    return  veri

def ekle_with_harf():
    print("Seçilecek Harfi Giriniz...(A, B, C, Ç, D, E, F, G, H, I, İ, J, K, L, M, N, O, Ö, P, Q, R, S, Ş, T, U, Ü, X, V, W, Y, Z, 1, 2, 3,4, 5, 6, 7, 8, 9, 0)")
    x=input()
    print(("İşleme Başlanıyor...."))
    #mağazanın adını alıyoruz
    veri = httpistek("https://www.n11.com/magazalar/" + x, 1)
    deg = re.findall("href=\"https://www.n11.com/magaza/(.*?)\"", str(veri).replace("\r\n", ""))
    try:
        os.mkdir("raw_data/" + x)
    except:
        pass
    print(("İşleme Başlandı"))
    for _ in deg:
        comm = httpistek("https://www.n11.com/magaza/" + _ + "/magaza-yorumlari", 5).decode('utf-8')
        #ürünleri daha rahat çekebilmek için satıcının idsini alıyoruz
        sellerid = re.findall("<input type=\"hidden\" id=\"sellerId\" value=\"(.*?)\"/>", comm)
        count = 2
        with open("raw_data/" + x + "/" + _ + ".csv", "a") as f:
            f.write("Comment|Score\n")
        f.close()

        while str(comm).find("reviews") != -1:
            comm = str(comm)[str(comm).find("<ul class=\"reviews\">") + 54:]
            while str(comm).find("productRev") != -1:
                isim = re.findall("<img width=\"140\" height=\"140\" alt=\"(.*?)\"", comm)
                comm = str(comm)[str(comm).find("productRev") + 10:]
                de = list()
                for t in range(3):
                    comm = str(comm)[:0] + str(comm)[str(comm).find("<span class=\"") + 13:]
                    de.append(str(comm)[:str(comm).find("\"") + 4])
                if any("icon\"></" in s for s in de):
                    continue
                comm = str(comm)[:0] + str(comm)[str(comm).find("<p >") + 4:]
                yorum = str(comm)[:str(comm).find("</p>")]
                # data=([isim[0],(icon_val(de[0])+icon_val(de[1])+icon_val(de[2]))/3,yorum.replace("\n", "").lstrip().rstrip()])
                try:
                    with open("raw_data/" + x + "/" + _ + ".csv", "a") as f:
                        #veri temizleme işlemi yapıyoruz
                        try:
                            yorum=veri_temizle(yorum)
                        except:
                            pass
                        print(remove_tags(emoji.demojize(html.unescape(str(
                            yorum + "|" + str(
                                (icon_val(de[0]) + icon_val(de[1]) + icon_val(de[2])) / 3)) + "\n"))))
                        f.write(remove_tags(emoji.demojize(html.unescape(str(
                            yorum + "|" + str(
                                (icon_val(de[0]) + icon_val(de[1]) + icon_val(de[2])) / 3)) + "\n"))))
                    f.close()
                except Exception as ex:
                    print(str(ex))
                    continue
            count += 1
            kontrol = 0
            while kontrol == 0:
                try:
                    comm = httpistek(
                        "https://www.n11.com/component/render/sellerShopFeedbacks?page=" + str(count) + "&sellerId=" +
                        sellerid[
                            0], 5).decode('utf-8')
                    print("kalinan sayfa " + str(count))
                    kontrol = 1
                except:
                    time.sleep(20)
                    kontrol = 0
    print("İşlem Bitti")

def ekle_with_link():
    print("Satıcının Linkini Giriniz...")
    t = input()
    print(("İşleme Başlanıyor...."))
    _ = t.split('/')[4]
    harf=_[0].upper()
    try:
        os.mkdir("raw_data/" + harf)
    except:
        pass
    print(("İşlem Başladı...."))
    comm = httpistek("https://www.n11.com/magaza/" + _ + "/magaza-yorumlari", 5).decode('utf-8')
    sellerid = re.findall("<input type=\"hidden\" id=\"sellerId\" value=\"(.*?)\"/>", comm)
    count = 2
    with open("raw_data/" + harf + "/" + _ + ".csv", "w",encoding=utf-8) as f:
        f.write("Comment|Score\n")
    f.close()

    while str(comm).find("reviews") != -1:
        comm = str(comm)[str(comm).find("<ul class=\"reviews\">") + 54:]
        while str(comm).find("productRev") != -1:
            isim = re.findall("<img width=\"140\" height=\"140\" alt=\"(.*?)\"", comm)
            comm = str(comm)[str(comm).find("productRev") + 10:]
            de = list()
            for t in range(3):
                comm = str(comm)[:0] + str(comm)[str(comm).find("<span class=\"") + 13:]
                de.append(str(comm)[:str(comm).find("\"") + 4])
            if any("icon\"></" in s for s in de):
                continue
            comm = str(comm)[:0] + str(comm)[str(comm).find("<p >") + 4:]
            yorum = str(comm)[:str(comm).find("</p>")]
            # data=([isim[0],(icon_val(de[0])+icon_val(de[1])+icon_val(de[2]))/3,yorum.replace("\n", "").lstrip().rstrip()])
            try:
                with open("raw_data/" + harf + "/" + _ + ".csv", "a") as f:
                    try:
                        yorum = veri_temizle(yorum)
                    except:
                        pass
                    print(remove_tags(emoji.demojize(html.unescape(str(
                        yorum.replace("\n", "").lstrip().rstrip() + "|" + str(
                            (icon_val(de[0]) + icon_val(de[1]) + icon_val(de[2])) / 3)) + "\n"))))
                    f.write(remove_tags(emoji.demojize(html.unescape(str(
                        yorum.replace("\n", "").lstrip().rstrip() + "|" + str(
                            (icon_val(de[0]) + icon_val(de[1]) + icon_val(de[2])) / 3)) + "\n"))))
                f.close()
            except Exception as ex:
                print(str(ex))
                continue
        count += 1
        kontrol = 0
        while kontrol == 0:
            try:
                comm = httpistek(
                    "https://www.n11.com/component/render/sellerShopFeedbacks?page=" + str(count) + "&sellerId=" +
                    sellerid[
                        0], 5).decode('utf-8')
                print("kalinan sayfa " + str(count))
                kontrol = 1
            except:
                time.sleep(20)
                kontrol = 0
    print("İşlem Bitti")

def ekle():
    print(("İşleme Başlanıyor...."))
    dizi_harf = ["A", "B", "C", "Ç", "D", "E", "F", "G", "H", "I", "İ", "J", "K", "L", "M", "N", "O", "Ö", "P", "Q", "R", "S", "Ş", "T", "U", "Ü", "X", "V", "W", "Y", "Z", "1", "2", "3","4", "5", "6", "7", "8", "9", "0"]
    for harf in dizi_harf:
        veri = httpistek("https://www.n11.com/magazalar/"+harf,1)
        deg = re.findall("href=\"https://www.n11.com/magaza/(.*?)\"", str(veri).replace("\r\n", ""))
        try:
            os.mkdir("raw_data/"+harf)
        except :
            pass
        print(("İşleme Başlatıldı...."))
        for _ in deg:
            comm=httpistek("https://www.n11.com/magaza/"+_+"/magaza-yorumlari", 5).decode('utf-8')
            sellerid = re.findall("<input type=\"hidden\" id=\"sellerId\" value=\"(.*?)\"/>", comm)
            count=2
            with open("raw_data/" + harf + "/" + _ + ".csv", "a") as f:
                f.write("Comment|Score\n")
            f.close()

            while str(comm).find("reviews") != -1:
                comm = str(comm)[str(comm).find("<ul class=\"reviews\">") + 54:]
                while str(comm).find("productRev") != -1:
                    isim = re.findall("<img width=\"140\" height=\"140\" alt=\"(.*?)\"", comm)
                    comm = str(comm)[str(comm).find("productRev") + 10:]
                    de=list()
                    for t in range(3):
                        comm = str(comm)[:0] + str(comm)[str(comm).find("<span class=\"") + 13:]
                        de.append(str(comm)[:str(comm).find("\"") + 4])
                    if any("icon\"></" in s for s in de):
                        continue
                    comm = str(comm)[:0] + str(comm)[str(comm).find("<p >") + 4:]
                    yorum = str(comm)[:str(comm).find("</p>")]
                    #data=([isim[0],(icon_val(de[0])+icon_val(de[1])+icon_val(de[2]))/3,yorum.replace("\n", "").lstrip().rstrip()])
                    try:
                        with open("raw_data/" + harf + "/" + _ + ".csv", "a",encoding=utf-8) as f:
                            try:
                                yorum = veri_temizle(yorum)
                            except:
                                pass
                            print(remove_tags(emoji.demojize(html.unescape(str(yorum.replace("\n", "").lstrip().rstrip()+"|"+str((icon_val(de[0])+icon_val(de[1])+icon_val(de[2]))/3))+"\n"))))
                            f.write(remove_tags(emoji.demojize(html.unescape(str(yorum.replace("\n", "").lstrip().rstrip()+"|"+str((icon_val(de[0])+icon_val(de[1])+icon_val(de[2]))/3))+"\n"))))
                        f.close()
                    except Exception as ex:
                        print(str(ex))
                        continue
                count+=1
                kontrol=0
                while kontrol==0:
                    try:
                        comm = httpistek(
                    "https://www.n11.com/component/render/sellerShopFeedbacks?page=" + str(count) + "&sellerId=" + sellerid[
                        0], 5).decode('utf-8')
                        print("kalinan sayfa "+str(count))
                        kontrol=1
                    except:
                        time.sleep(20)
                        kontrol=0
    print("İşlem Bitti")

def main():
    while True:
        print("Yapılacak İşlemi Seçini:\n1-Tüm Datayı Çek\n2-Harfe Göre Seç\n3-Mağaza Linkine Göre Seç\n4-Çıkış")
        try:
            x = int(input("İşlem ID:"))
            if x>4 and x<1:
                print("Hatalı Giriş Tekrar Seçim Yapınız...")
                continue
            else:
                if x==1:
                    ekle()
                elif x==2:
                    ekle_with_harf()
                    print("İşleminiz Gerçekleşti Yeni bri İşlem Seçiniz...")
                elif x==3:
                    ekle_with_link()
                    print("İşleminiz Gerçekleşti Yeni bri İşlem Seçiniz...")
                else:
                    break
        except:
            print("Hatalı Giriş Tekrar Seçim Yapınız...")

if __name__ == '__main__':
    main()
