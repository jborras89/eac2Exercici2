from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
 
class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()


    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        #cls.selenium.quit()
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

  
        # Comprovar que pot veure i accedir a la pàgina de creació d'usuaris
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/auth/user/add/'))
        self.assertIn("Add user", self.selenium.title)
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("staff")

        password1_input = self.selenium.find_element(By.NAME, "password1")
        password1_input.send_keys("password_seguro123")

        password2_input = self.selenium.find_element(By.NAME, "password2")
        password2_input.send_keys("password_seguro123")

        # Enviar el formulari per crear l'usuari
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()
        
        # Comprovar que l'usuari 'staff' ha estat creat correctament redirigint-nos a la pàgina d'edició
        self.assertIn("Change user", self.selenium.title)

        # Assignar permisos a l'usuari 'staff' per veure i crear altres usuaris
        user_permissions = self.selenium.find_elements(By.NAME, "user_permissions")
        for permission in user_permissions:
            permission_title = permission.get_attribute("title")
            if permission_title == "Can add user" or permission_title == "Can view user":
               permission.click()
        
        # Guardar els canvis a l'usuari 'staff' amb els permisos seleccionats
        self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()
        
        # Confirmar que s'ha desat correctament
        #self.assertIn("The user “staff” was changed successfully.", self.selenium.page_source)

        # Comprovar que estem de nou a la llista d'usuaris, que indica que s'ha desat correctament
        self.assertIn("/admin/auth/user/", self.selenium.current_url)
        
        # 4. Tancar sessió de l'usuari admin
        try:
            self.selenium.find_element(By.XPATH,"//a[text()='Log out']")
            assert False, "Trobat element que NO hi ha de ser"
        except NoSuchElementException:
            pass
        self.selenium.find_element(By.XPATH,"//button[text()='Log out']")

        # 5. Iniciar sessió amb l'usuari 'staff'
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        
