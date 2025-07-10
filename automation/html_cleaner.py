from bs4 import BeautifulSoup

class HTMLCleaner:
    @staticmethod
    def clean(html: str) -> str:
        """Clean HTML using BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unnecessary elements
        for tag in soup(['script', 'style', 'noscript', 'meta', 'link']):
            tag.decompose()
            
        # Simplify attributes
        for tag in soup.find_all(True):
            tag.attrs = {k: v for k, v in tag.attrs.items() 
                        if k in ['id', 'name', 'class', 'type', 'href', 'aria-label', 
                                 'data-testid', 'placeholder', 'for', 'role']}
        
        return str(soup.body) if soup.body else str(soup)[:20000]