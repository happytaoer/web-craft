"""
IP Address Spider - Specialized for extracting IP addresses and geolocation information
"""
from typing import Dict, Any
from lxml import html
from .base_spider import BaseSpider


class IpSpider(BaseSpider):
    """
    IP Address Spider Implementation
    
    Specialized for extracting IP addresses and related information from websites like ip.me:
    - IP address extraction
    - Geolocation information
    - ISP information
    - Latitude and longitude coordinates
    """
    
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse web content using XPath to extract IP address and geolocation information
        
        Args:
            raw_content: Raw HTML/text content
            url: Requested URL
            headers: Response headers
            
        Returns:
            Dictionary of extracted IP address and geolocation data
        """
        try:
            # Parse HTML
            tree = html.fromstring(raw_content)
            
            data = {}
            
            # Extract IP address - get from input element's value attribute
            ip_xpath = '//input[@name="ip"]/@value'
            ip_elements = tree.xpath(ip_xpath)
            if ip_elements:
                data['ip_address'] = ip_elements[0]
            
            # Extract geolocation information - get from table
            location_data = {}
            
            # City
            city_xpath = '//th[text()="City:"]/following-sibling::td/code/text()'
            city = tree.xpath(city_xpath)
            if city:
                location_data['city'] = city[0]
            
            # Country
            country_xpath = '//th[text()="Country:"]/following-sibling::td/code/text()'
            country = tree.xpath(country_xpath)
            if country:
                location_data['country'] = country[0]
            
            # Country code
            country_code_xpath = '//th[text()="Country Code:"]/following-sibling::td/code/text()'
            country_code = tree.xpath(country_code_xpath)
            if country_code:
                location_data['country_code'] = country_code[0]
            
            # Latitude
            latitude_xpath = '//th[text()="Latitude:"]/following-sibling::td[@class="latitude"]/code/text()'
            latitude = tree.xpath(latitude_xpath)
            if latitude:
                location_data['latitude'] = float(latitude[0])
            
            # Longitude
            longitude_xpath = '//th[text()="Longitude:"]/following-sibling::td[@class="longitude"]/code/text()'
            longitude = tree.xpath(longitude_xpath)
            if longitude:
                location_data['longitude'] = float(longitude[0])
            
            # Postal code
            postal_code_xpath = '//th[text()="Postal Code:"]/following-sibling::td/code/text()'
            postal_code = tree.xpath(postal_code_xpath)
            if postal_code:
                location_data['postal_code'] = postal_code[0]
            
            # Organization/ISP
            organization_xpath = '//th[text()="Organization:"]/following-sibling::td/code/text()'
            organization = tree.xpath(organization_xpath)
            if organization:
                location_data['organization'] = organization[0]
            
            # ASN
            asn_xpath = '//th[text()="ASN:"]/following-sibling::td/code/text()'
            asn = tree.xpath(asn_xpath)
            if asn:
                location_data['asn'] = asn[0]
            
            # ISP name
            isp_xpath = '//th[text()="ISP Name:"]/following-sibling::td/code/text()'
            isp = tree.xpath(isp_xpath)
            if isp:
                location_data['isp_name'] = isp[0]
            
            # Add geolocation information to main data
            if location_data:
                data['location'] = location_data
            
            # Extract page title
            title_xpath = '//title/text()'
            title = tree.xpath(title_xpath)
            if title:
                data['page_title'] = title[0]
            
            return data
            
        except Exception as e:
            # If XPath parsing fails, return error information
            return {
                'error': f'Parsing failed: {str(e)}',
                'raw_content_preview': raw_content[:500] if raw_content else 'No content'
            }
