"""
IP地址爬虫 - 专门用于提取IP地址和地理位置信息
"""
from typing import Dict, Any
from lxml import html
from .base_spider import BaseSpider


class IpSpider(BaseSpider):
    """
    IP地址爬虫实现
    
    专门用于从ip.me等网站提取IP地址和相关信息：
    - IP地址提取
    - 地理位置信息
    - ISP信息
    - 经纬度坐标
    """
    
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        使用XPath解析网页内容，提取IP地址和地理位置信息
        
        Args:
            raw_content: 原始HTML/文本内容
            url: 请求的URL
            headers: 响应头信息
            
        Returns:
            提取的IP地址和地理位置数据字典
        """
        try:
            # 解析HTML
            tree = html.fromstring(raw_content)
            
            data = {}
            
            # 提取IP地址 - 从input元素的value属性中获取
            ip_xpath = '//input[@name="ip"]/@value'
            ip_elements = tree.xpath(ip_xpath)
            if ip_elements:
                data['ip_address'] = ip_elements[0]
            
            # 提取地理位置信息 - 从表格中获取
            location_data = {}
            
            # 城市
            city_xpath = '//th[text()="City:"]/following-sibling::td/code/text()'
            city = tree.xpath(city_xpath)
            if city:
                location_data['city'] = city[0]
            
            # 国家
            country_xpath = '//th[text()="Country:"]/following-sibling::td/code/text()'
            country = tree.xpath(country_xpath)
            if country:
                location_data['country'] = country[0]
            
            # 国家代码
            country_code_xpath = '//th[text()="Country Code:"]/following-sibling::td/code/text()'
            country_code = tree.xpath(country_code_xpath)
            if country_code:
                location_data['country_code'] = country_code[0]
            
            # 纬度
            latitude_xpath = '//th[text()="Latitude:"]/following-sibling::td[@class="latitude"]/code/text()'
            latitude = tree.xpath(latitude_xpath)
            if latitude:
                location_data['latitude'] = float(latitude[0])
            
            # 经度
            longitude_xpath = '//th[text()="Longitude:"]/following-sibling::td[@class="longitude"]/code/text()'
            longitude = tree.xpath(longitude_xpath)
            if longitude:
                location_data['longitude'] = float(longitude[0])
            
            # 邮政编码
            postal_code_xpath = '//th[text()="Postal Code:"]/following-sibling::td/code/text()'
            postal_code = tree.xpath(postal_code_xpath)
            if postal_code:
                location_data['postal_code'] = postal_code[0]
            
            # 组织/ISP
            organization_xpath = '//th[text()="Organization:"]/following-sibling::td/code/text()'
            organization = tree.xpath(organization_xpath)
            if organization:
                location_data['organization'] = organization[0]
            
            # ASN
            asn_xpath = '//th[text()="ASN:"]/following-sibling::td/code/text()'
            asn = tree.xpath(asn_xpath)
            if asn:
                location_data['asn'] = asn[0]
            
            # ISP名称
            isp_xpath = '//th[text()="ISP Name:"]/following-sibling::td/code/text()'
            isp = tree.xpath(isp_xpath)
            if isp:
                location_data['isp_name'] = isp[0]
            
            # 将地理位置信息添加到主数据中
            if location_data:
                data['location'] = location_data
            
            # 提取页面标题
            title_xpath = '//title/text()'
            title = tree.xpath(title_xpath)
            if title:
                data['page_title'] = title[0]
            
            return data
            
        except Exception as e:
            # 如果XPath解析失败，返回错误信息
            return {
                'error': f'解析失败: {str(e)}',
                'raw_content_preview': raw_content[:500] if raw_content else 'No content'
            }
