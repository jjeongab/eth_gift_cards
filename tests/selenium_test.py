from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pytest

class TestGiftCardUI:
    def setup_method(self):
        """Set up test browser"""
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # For MetaMask mocking, we'll use a regular browser
        # In real testing, you'd use a MetaMask extension or mock
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("http://localhost:3000")  # Adjust URL as needed
        self.wait = WebDriverWait(self.driver, 10)
    
    def teardown_method(self):
        """Clean up after tests"""
        self.driver.quit()
    
    def mock_connect_wallet(self):
        """Mock wallet connection for testing"""
        # In real testing, you'd automate MetaMask
        # For now, we'll simulate the connection
        connect_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "connectWallet"))
        )
        
        # Inject mock ethereum object
        self.driver.execute_script("""
            window.ethereum = {
                selectedAddress: '0x1234567890123456789012345678901234567890',
                request: async ({ method }) => {
                    if (method === 'eth_requestAccounts') {
                        return ['0x1234567890123456789012345678901234567890'];
                    }
                    return null;
                }
            };
        """)
        
        connect_button.click()
        time.sleep(1)
    
    def test_wallet_connection(self):
        """Test wallet connection UI"""
        # Check initial state
        wallet_status = self.driver.find_element(By.ID, "walletStatus")
        assert "Not connected" in wallet_status.text
        
        # Mock connect
        self.mock_connect_wallet()
        
        # Check connected state
        wallet_status = self.driver.find_element(By.ID, "walletStatus")
        assert "Connected:" in wallet_status.text
    
    def test_buy_gift_card_ui(self):
        """Test buying a gift card through UI"""
        self.mock_connect_wallet()
        
        # Fill in buy form
        code_input = self.driver.find_element(By.ID, "buyCode")
        code_input.send_keys("UITEST123")
        
        amount_input = self.driver.find_element(By.ID, "ethAmount")
        amount_input.send_keys("0.01")
        
        # Mock the contract interaction
        self.driver.execute_script("""
            window.mockTransaction = true;
            // Override the contract buy function
            if (window.contract) {
                window.contract.buy = async () => {
                    return { wait: async () => ({ status: 1 }) };
                };
            }
        """)
        
        # Click buy button
        buy_button = self.driver.find_element(By.XPATH, "//button[text()='Buy Gift Card']")
        buy_button.click()
        
        # Check for status message
        time.sleep(1)
        status = self.driver.find_element(By.ID, "buyStatus")
        assert status.is_displayed()
    
    def test_redeem_gift_card_ui(self):
        """Test redeeming a gift card through UI"""
        self.mock_connect_wallet()
        
        # Fill in redeem form
        code_input = self.driver.find_element(By.ID, "redeemCode")
        code_input.send_keys("UITEST123")
        
        # Mock the contract interaction
        self.driver.execute_script("""
            window.mockTransaction = true;
            // Override the contract redeem function
            if (window.contract) {
                window.contract.redeem = async () => {
                    return { wait: async () => ({ status: 1 }) };
                };
            }
        """)
        
        # Click redeem button
        redeem_button = self.driver.find_element(By.XPATH, "//button[text()='Redeem Gift Card']")
        redeem_button.click()
        
        # Check for status message
        time.sleep(1)
        status = self.driver.find_element(By.ID, "redeemStatus")
        assert status.is_displayed()
    
    def test_form_validation(self):
        """Test form validation"""
        self.mock_connect_wallet()
        
        # Try to buy without entering data
        buy_button = self.driver.find_element(By.XPATH, "//button[text()='Buy Gift Card']")
        buy_button.click()
        
        # Check for error message
        time.sleep(1)
        status = self.driver.find_element(By.ID, "buyStatus")
        assert "Please enter both code and ETH amount" in status.text
        
        # Test minimum amount validation
        code_input = self.driver.find_element(By.ID, "buyCode")
        code_input.send_keys("TEST")
        
        amount_input = self.driver.find_element(By.ID, "ethAmount")
        amount_input.send_keys("0.0005")  # Below minimum
        
        buy_button.click()
        time.sleep(1)
        assert "Minimum gift card value is 0.001 ETH" in status.text
    
    def test_ui_elements_present(self):
        """Test that all UI elements are present"""
        # Check main elements
        assert self.driver.find_element(By.TAG_NAME, "h1").text == "🎁 Ethereum Gift Card System"
        
        # Check buy section
        assert self.driver.find_element(By.ID, "buyCode")
        assert self.driver.find_element(By.ID, "ethAmount")
        
        # Check redeem section
        assert self.driver.find_element(By.ID, "redeemCode")
        
        # Check buttons
        assert self.driver.find_element(By.ID, "connectWallet")
        assert self.driver.find_element(By.XPATH, "//button[text()='Buy Gift Card']")
        assert self.driver.find_element(By.XPATH, "//button[text()='Redeem Gift Card']")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])