import requests
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from database.models import Contract, ScrapingLog
import logging
import os

logger = logging.getLogger(__name__)

class ContractScraper:
    def __init__(self, db: Session):
        self.db = db
        self.target_naics = ["488510", "541614", "332311", "492110", "336611"]
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    async def scrape_all_sources(self) -> Dict[str, int]:
        """Scrape all contract sources and return summary"""
        results = {}
        
        # Scrape SAM.gov
        try:
            sam_results = await self.scrape_sam_gov()
            results['sam_gov'] = sam_results
            self._log_scraping_result('SAM.gov', sam_results['contracts_added'], sam_results['contracts_found'], 'success')
        except Exception as e:
            logger.error(f"SAM.gov scraping failed: {str(e)}")
            self._log_scraping_result('SAM.gov', 0, 0, 'error', str(e))
            results['sam_gov'] = {'contracts_found': 0, 'contracts_added': 0, 'error': str(e)}

        # Scrape Miami-Dade County
        try:
            miami_results = await self.scrape_miami_dade()
            results['miami_dade'] = miami_results
            self._log_scraping_result('Miami-Dade', miami_results['contracts_added'], miami_results['contracts_found'], 'success')
        except Exception as e:
            logger.error(f"Miami-Dade scraping failed: {str(e)}")
            self._log_scraping_result('Miami-Dade', 0, 0, 'error', str(e))
            results['miami_dade'] = {'contracts_found': 0, 'contracts_added': 0, 'error': str(e)}

        # Scrape Unison Marketplace
        try:
            unison_results = await self.scrape_unison_marketplace()
            results['unison'] = unison_results
            self._log_scraping_result('Unison', unison_results['contracts_added'], unison_results['contracts_found'], 'success')
        except Exception as e:
            logger.error(f"Unison scraping failed: {str(e)}")
            self._log_scraping_result('Unison', 0, 0, 'error', str(e))
            results['unison'] = {'contracts_found': 0, 'contracts_added': 0, 'error': str(e)}

        return results

    async def scrape_sam_gov(self) -> Dict[str, int]:
        """Scrape contracts from SAM.gov"""
        contracts_found = 0
        contracts_added = 0
        
        base_url = "https://sam.gov/api/prod/sgs/v1/search/"
        
        for naics_code in self.target_naics:
            try:
                # SAM.gov API parameters
                params = {
                    'index': 'opp',
                    'q': f'naicsCode:"{naics_code}"',
                    'page': 0,
                    'size': 25,
                    'sort': '-modifiedDate',
                    'mode': 'search'
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
                
                response = requests.get(base_url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    opportunities = data.get('_embedded', {}).get('results', [])
                    
                    for opp in opportunities:
                        contracts_found += 1
                        
                        # Extract contract data
                        contract_data = {
                            'title': opp.get('title', ''),
                            'agency': opp.get('department', {}).get('name', ''),
                            'naics_code': naics_code,
                            'value': self._parse_value(opp.get('awardCeiling')),
                            'deadline': self._parse_date(opp.get('responseDeadLine')),
                            'status': 'active',
                            'opportunity_score': self._calculate_opportunity_score(opp),
                            'notes': f"Source: SAM.gov | ID: {opp.get('noticeId', '')}"
                        }
                        
                        # Check if contract already exists
                        existing = self.db.query(Contract).filter(
                            Contract.title == contract_data['title'],
                            Contract.agency == contract_data['agency']
                        ).first()
                        
                        if not existing:
                            new_contract = Contract(**contract_data)
                            self.db.add(new_contract)
                            contracts_added += 1
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping SAM.gov for NAICS {naics_code}: {str(e)}")
                continue
        
        self.db.commit()
        return {'contracts_found': contracts_found, 'contracts_added': contracts_added}

    async def scrape_miami_dade(self) -> Dict[str, int]:
        """Scrape contracts from Miami-Dade County portal"""
        contracts_found = 0
        contracts_added = 0
        
        try:
            url = "https://www.miamidade.gov/procurement/solicitations.asp"
            
            self.driver.get(url)
            await asyncio.sleep(3)
            
            # Look for contract listings
            contract_elements = self.driver.find_elements(By.CSS_SELECTOR, ".solicitation-item, .bid-item, tr")
            
            for element in contract_elements[:25]:  # Limit to 25 items
                try:
                    contracts_found += 1
                    
                    # Extract contract information (this would need to be customized based on actual HTML structure)
                    title_elem = element.find_element(By.CSS_SELECTOR, "td:first-child, .title, h3, a")
                    title = title_elem.text.strip() if title_elem else "Miami-Dade Contract"
                    
                    # Try to extract deadline
                    deadline_text = element.text
                    deadline = self._extract_date_from_text(deadline_text)
                    
                    contract_data = {
                        'title': title,
                        'agency': 'Miami-Dade County',
                        'naics_code': '541614',  # Default to logistics consulting
                        'value': None,
                        'deadline': deadline,
                        'status': 'active',
                        'opportunity_score': 6,  # Default score for Miami-Dade
                        'notes': f"Source: Miami-Dade County Portal"
                    }
                    
                    # Check if contract already exists
                    existing = self.db.query(Contract).filter(
                        Contract.title == contract_data['title'],
                        Contract.agency == contract_data['agency']
                    ).first()
                    
                    if not existing and title and len(title) > 10:
                        new_contract = Contract(**contract_data)
                        self.db.add(new_contract)
                        contracts_added += 1
                        
                except Exception as e:
                    continue
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error scraping Miami-Dade: {str(e)}")
        
        return {'contracts_found': contracts_found, 'contracts_added': contracts_added}

    async def scrape_unison_marketplace(self) -> Dict[str, int]:
        """Scrape contracts from Unison Marketplace"""
        contracts_found = 0
        contracts_added = 0
        
        try:
            # Unison Marketplace URL (this would need to be the actual URL)
            url = "https://www.unison-marketplace.com/opportunities"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for contract listings (customize selectors based on actual site)
                contract_elements = soup.find_all(['div', 'tr', 'li'], class_=lambda x: x and ('opportunity' in x.lower() or 'contract' in x.lower()))
                
                for element in contract_elements[:20]:  # Limit to 20 items
                    try:
                        contracts_found += 1
                        
                        title = element.get_text().strip()[:200] if element.get_text() else "Unison Opportunity"
                        
                        contract_data = {
                            'title': title,
                            'agency': 'Various Agencies',
                            'naics_code': '488510',  # Default to freight transportation
                            'value': None,
                            'deadline': None,
                            'status': 'active',
                            'opportunity_score': 5,  # Default score for Unison
                            'notes': f"Source: Unison Marketplace"
                        }
                        
                        # Check if contract already exists
                        existing = self.db.query(Contract).filter(
                            Contract.title == contract_data['title'],
                            Contract.agency == contract_data['agency']
                        ).first()
                        
                        if not existing and title and len(title) > 10:
                            new_contract = Contract(**contract_data)
                            self.db.add(new_contract)
                            contracts_added += 1
                            
                    except Exception as e:
                        continue
                
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error scraping Unison Marketplace: {str(e)}")
        
        return {'contracts_found': contracts_found, 'contracts_added': contracts_added}

    def _calculate_opportunity_score(self, opportunity: Dict) -> int:
        """Calculate opportunity score based on various factors"""
        score = 5  # Base score
        
        # Increase score based on award ceiling
        ceiling = opportunity.get('awardCeiling')
        if ceiling:
            try:
                value = float(ceiling)
                if value > 1000000:
                    score += 3
                elif value > 500000:
                    score += 2
                elif value > 100000:
                    score += 1
            except:
                pass
        
        # Increase score for competitive opportunities
        if opportunity.get('competitionType') == 'Full and Open Competition':
            score += 1
        
        # Increase score based on response time
        deadline = opportunity.get('responseDeadLine')
        if deadline:
            try:
                deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                days_until_deadline = (deadline_date - datetime.now()).days
                if days_until_deadline > 30:
                    score += 1
                elif days_until_deadline < 7:
                    score -= 1
            except:
                pass
        
        return min(max(score, 1), 10)  # Keep score between 1-10

    def _parse_value(self, value_str: Optional[str]) -> Optional[float]:
        """Parse contract value from string"""
        if not value_str:
            return None
        
        try:
            # Remove currency symbols and commas
            clean_value = value_str.replace('$', '').replace(',', '').strip()
            return float(clean_value)
        except:
            return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date from string"""
        if not date_str:
            return None
        
        try:
            # Handle ISO format dates
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text using common patterns"""
        import re
        
        # Common date patterns
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}-\d{1,2}-\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group()
                    if '/' in date_str:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    elif '-' in date_str and len(date_str) == 10:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                    elif '-' in date_str:
                        return datetime.strptime(date_str, '%m-%d-%Y')
                except:
                    continue
        
        return None

    def _log_scraping_result(self, source: str, contracts_added: int, contracts_found: int, status: str, error_message: str = None):
        """Log scraping results to database"""
        log_entry = ScrapingLog(
            source=source,
            contracts_found=contracts_found,
            contracts_added=contracts_added,
            status=status,
            error_message=error_message
        )
        self.db.add(log_entry)
        self.db.commit()

# Celery task for scheduled scraping
async def run_daily_scraping(db: Session):
    """Run daily contract scraping"""
    scraper = ContractScraper(db)
    try:
        results = await scraper.scrape_all_sources()
        logger.info(f"Daily scraping completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Daily scraping failed: {str(e)}")
        raise
    finally:
        del scraper