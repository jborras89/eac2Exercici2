from django.test import TestCase

# Create your tests here.

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
 
class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    fixtures = ['testdb.json',]
 
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
 
    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        cls.selenium.quit()
        super().tearDownClass()
 
    def test_login(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
 
        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
 
        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()
 
        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

        # Creem un nou usuari amb permisos de "staff"
        try:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Users"))
            )
            self.selenium.find_element(By.LINK_TEXT, "Users").click()
            
            # Esperem que el botó "Add user" estigui disponible
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Add user"))
            )
            self.selenium.find_element(By.LINK_TEXT, "Add user").click()
        except TimeoutException:
            print("L'element 'Add user' no es va trobar a temps.")
            print(self.selenium.page_source)  # Imprimir contingut de la pàgina per depuració
        #self.selenium.find_element(By.LINK_TEXT, "Users").click()
        #self.selenium.find_element(By.LINK_TEXT, "Add user").click()

        # Completem el formulari de creació d'usuari
        self.selenium.find_element(By.NAME, "username").send_keys("staff")
        self.selenium.find_element(By.NAME, "password1").send_keys("staff123")
        self.selenium.find_element(By.NAME, "password2").send_keys("staff123")
        self.selenium.find_element(By.NAME, "password2").send_keys(Keys.RETURN)

        # Assignem permisos de staff
        self.selenium.find_element(By.NAME, "is_staff").click()
        self.selenium.find_element(By.NAME, "_save").click()

        # Verifiquem que l'usuari s'ha creat correctament
        self.assertIn("The user “usuari_staff_test” was added successfully.", self.selenium.page_source)

        # Tancar la sessió d'administrador
        self.selenium.find_element(By.LINK_TEXT, "Log out").click()

        # Iniciem sessió amb l'usuari staff creat anteriorment
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("staff")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("staff123")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Comprovem que pot veure "Users" però no "Questions"
        self.assertIn("Users", self.selenium.page_source)
        self.assertNotIn("Questions", self.selenium.page_source)

    def test_staff_user_cannot_access_questions(self):
        # Comprova que l'usuari no pot accedir a la secció de "Questions"
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/app_name/question/'))  # Canvia 'app_name' pel nom de la teva aplicació

        # Comprovem que la pàgina indica que no té permisos
        self.assertIn("permission denied", self.selenium.page_source.lower())

