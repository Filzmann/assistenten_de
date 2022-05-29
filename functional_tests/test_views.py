import time
from unittest import skip

from selenium.webdriver.common.keys import Keys
from functional_tests.base import FunctionalTest


class NewVisitorTest(FunctionalTest):

    def test_user_kann_kann_sich_einloggen(self):
        # er surft damit die Adresse der Assistenten-Software an
        self.browser.get(self.live_server_url)
        # Einmal auf der Seite gelandet stellt er fest, dass im Titel das Wort "Assistenten" steht
        self.assertIn('Assistenten', self.browser.title)

        # Simon möchte sich gern einloggen

        # dafür sucht er das login-feld an und gibt seinen Nutzernamen ein
        loginbox = self.browser.find_element_by_name('username')
        self.assertEqual(
            loginbox.get_attribute('placeholder'),
            'Username'
        )
        loginbox.send_keys('simon')

        # dann klickt er in das Passwortfeld und gibt sein passwort ein
        passwortbox = self.browser.find_element_by_name('password')
        self.assertEqual(
            passwortbox.get_attribute('placeholder'),
            'Password'
        )
        passwortbox.send_keys('22test00')
        # danach klickt er auf den Login-button oder drückt Enter
        passwortbox.send_keys(Keys.ENTER)
        time.sleep(5)

        # nachdem er eingeloggt ist sieht er, dass oben rechts sein benutzername "simon" steht
        hauptmenu = self.browser.find_element_by_id('navbar')
        rows = hauptmenu.find_elements_by_tag_name('a')
        self.assertTrue(any(row.text == 'simon' for row in rows))

    @skip
    def test_user_navigiert_zu_Assistent_bearbeiten_und_kann_seine_daten_aendern(self):
        # Simon sieht das App-Menü auf der rechten Seite
        self.browser.find_element_by_link_text('Menue').click()
        # er möchte gerne seine Assistentendaten bearbeiten. Dafür klickt er auf "Nutzerkonto/Assistent bearbeiten"
        self.browser.find_element_by_link_text('Nutzerkonto/Assistent bearbeiten').click()
        input_name = self.browser.find_element_by_id('id_name')
        # er kann dort seinen Namen, Vornamen, Email und Einstellungsdatum eingeben
        input_name.send_keys('Beyer')
        input_vorname = self.browser.find_element_by_id('id_vorname')
        input_vorname.send_keys('Simon')
        input_email = self.browser.find_element_by_id('id_email')
        input_email.send_keys('simonbeyer79@gmail.com')
        input_einstellungsdatum = self.browser.find_element_by_id('id_einstellungsdatum')
        input_einstellungsdatum.send_keys('simonbeyer79@gmail.com')
        # Dann klickt er auf Abschicken/Enter.
        input_einstellungsdatum.send_keys(Keys.ENTER)
        # Es folgt eine Erfolgsmeldung
        time.sleep(1)
        self.browser.find_element_by_id('success message')

        # Simon ist weiterhin auf der gleichen Seite

    @skip
    def test_user_kann_sich_wieder_ausloggen(self):
        # Simon ist vorbildlich und loggt sich vor dem verlassen der Seite wieder aus
        pass

    def test_fail(self):
        self.fail('Mach den Test fertsch!')
