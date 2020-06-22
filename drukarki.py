import tornado.ioloop
import tornado.web
import json
import string

drukarki=[]
liczba_drukarek=0
wyswietlane_domyslnie=1

html_poczatek="""
          <!DOCTYPE html>
          <html lang='en'>
          <head>
            <meta charset='UTF-8'>
            <title>ALL USERS</title>
          </head>
          <body>
          """
html_koniec="""
          </body>
          </html>
          """

def dodaj_drukarke(drukarka):
    global liczba_drukarek
    drukarki.append(drukarka)
    liczba_drukarek+=1
    
class NotFoundHandler(tornado.web.RequestHandler):
    def prepare(self):  # for all methods
        raise tornado.web.HTTPError(
            status_code=404,
            reason="Invalid resource path."
        )
    
class Main_Handler(tornado.web.RequestHandler):
  def get(self):
    self.set_header("Content-Type","text/html")
    self.write("<b>INSTRUKCJA</b><br/><br/>")
    self.write("pod sciezka /drukarki mozemy wywolywac metody RESTowe GET/POST/DELETE/PUT/PATCH<br/><br/>")
    self.write("powyzsza sciezka moze przyjmowac argumenty personalizujace sposob wyswietlania zasobow:")
    self.write("- /?na_stronach="+ str(wyswietlane_domyslnie)+ "<br/><br/>- liczba elementow na stronie<br/><br/>")
    self.write("- ?strona= - domyslnie 1")
    
class User_Handler(tornado.web.RequestHandler):
  @tornado.web.removeslash
  def get(self,id):
      if id!="":
        wartosc_id=int(id)
        czy_istnieje=False
        print(wartosc_id)
        for obiekt in drukarki:
          if obiekt["id"]==wartosc_id:
            czy_istnieje=True
            self.write(obiekt)
            self.set_header("Content-Type","text/html")
        if not czy_istnieje:
          self.set_status(404)
      else:        
        numer_strony=int(self.get_argument("strona",1))
        na_stronie=int(self.get_argument("na_stronach",wyswietlane_domyslnie))
        drukarki_przez_strony=divmod(liczba_drukarek,na_stronie)
        wszystkich_stron=drukarki_przez_strony[0]
        if drukarki_przez_strony[1]:
         wszystkich_stron+=1
        if numer_strony>wszystkich_stron:
           numer_strony=1
        for obiekt_2 in range(0,na_stronie):
          elem_id=((numer_strony-1)*na_stronie)+obiekt_2
          if elem_id>=liczba_drukarek:
            self.set_status(404,"Not found")
            break
          self.write(drukarki[elem_id])
          self.set_header("Content-Type","text/html")
          self.write("<br/>")
        if elem_id+1<liczba_drukarek:
          wartosc="<br/> <a href='/drukarki?strona={}&na_stronach={}'>Next_Page</a>".format(numer_strony+1,na_stronie)
          self.write(wartosc)
        if elem_id-na_stronie>=0:
          wartosc="<br/> <a href='/drukarki?strona={}&na_stronach={}'>Prev_Page</a>".format(numer_strony-1,na_stronie)
          self.write(wartosc)
          
  def post(self,flaga):
        przeslany_obiekt=(json.loads(self.request.body))
        if isinstance(przeslany_obiekt,dict):
          dodaj_drukarke(przeslany_obiekt)
        else:
          for obiekt in przeslany_obiekt:
            dodaj_drukarke(obiekt)
            
  def delete(self,id):
    global liczba_drukarek
    do_usuniecia=-1
    for obiekt in drukarki:
        if obiekt["id"]==int(id):
            do_usuniecia=obiekt
    if do_usuniecia["id"]>=0:
        drukarki.remove(do_usuniecia)
        liczba_drukarek-=1
        
  def put (self,id):
    temp_id=int(id)
    do_aktualizacji=None
    przeslany_obiekt=json.loads(self.request.body)
    for obiekt in drukarki:
      if obiekt["id"]==temp_id:
        do_aktualizacji=obiekt
    id_2=drukarki.index(do_aktualizacji)
    if id_2>=0:
      drukarki[id_2]=przeslany_obiekt
      
  def patch(self,id):
      temp_id=int(id)
      przeslany_obiekt=json.loads(self.request.body)
      przeslany_obiekt_dict=dict(przeslany_obiekt) #funckja do obslugi JSON
      przeslany_obiekt_dict_keys=przeslany_obiekt_dict.keys()

      for obiekt in drukarki:
        if(obiekt["id"]==temp_id):
          do_aktualizacji=obiekt
      id_2=drukarki.index(do_aktualizacji)
      if(id_2>=0):
        for key_str in przeslany_obiekt_dict_keys:
          drukarki[id_2][key_str]=przeslany_obiekt_dict[key_str]

application = tornado.web.Application([
    (r"/", Main_Handler),
    (r"/drukarki\/*([0-9]*)", User_Handler)
],default_handler_class=NotFoundHandler)

if __name__ == "__main__":
    drukarka1={
    "id": 1,
    "Firma": "HP",
    "Rok produkcji": 2003,
    "Kolorowa": False
    }
    drukarka2={
    "id": 2,
    "Firma": "RICOH",
    "Rok produkcji": 2017,
    "Kolorowa": True
    }
    drukarka3={
    "id": 3,
    "Firma": "Kyocera",
    "Rok produkcji": 2009,
    "Kolorowa": True
    }
    drukarka4={
    "id": 4,
    "Firma": "Brother",
    "Rok produkcji": 2017,
    "Kolorowa": True
    }
    dodaj_drukarke(drukarka1)
    dodaj_drukarke(drukarka2)
    dodaj_drukarke(drukarka3)
    dodaj_drukarke(drukarka4)
    print('Server is running...')
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
