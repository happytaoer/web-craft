"""
Hacker News Spider - Specialized for extracting news items from Hacker News
"""
from typing import Dict, Any, List
from lxml import html
from spiders.core.base_spider import BaseSpider


class HackerNewsSpider(BaseSpider):
    """
    Hacker News Spider Implementation
    
    Specialized for extracting news items from Hacker News homepage:
    - Article titles and URLs
    - Rankings
    - Points/scores
    - Authors
    - Timestamps
    - Comment counts
    - Site sources
    """
    
    name = "hackernews"
    
    # Default URL for Hacker News homepage
    start_url = "https://news.ycombinator.com"
    
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse Hacker News HTML content using XPath to extract news items
        
        Args:
            raw_content: Raw HTML content
            url: Requested URL
            headers: Response headers
            
        Returns:
            Dictionary containing extracted news items and metadata
        """
        try:
            # Parse HTML
            tree = html.fromstring(raw_content)
            
            data = {}

            # Extract user information from header
            user_info = {}
            username_xpath = '//a[@id="me"]/text()'
            username = tree.xpath(username_xpath)
            if username:
                user_info['username'] = username[0]
            
            karma_xpath = '//span[@id="karma"]/text()'
            karma = tree.xpath(karma_xpath)
            if karma:
                user_info['karma'] = int(karma[0])
            
            if user_info:
                data['user_info'] = user_info
            
            # Extract news items
            news_items = []
            
            # Get all story rows (class="athing")
            story_rows = tree.xpath('//tr[@class="athing submission"]')
            
            for story in story_rows:
                item = {}
                
                # Extract story ID
                story_id = story.get('id')
                if story_id:
                    item['id'] = story_id
                
                # Extract rank
                rank_xpath = './/span[@class="rank"]/text()'
                rank = story.xpath(rank_xpath)
                if rank:
                    item['rank'] = int(rank[0].rstrip('.'))
                
                # Extract title and URL
                title_xpath = './/span[@class="titleline"]/a[1]'
                title_elem = story.xpath(title_xpath)
                if title_elem:
                    item['title'] = title_elem[0].text_content()
                    item['url'] = title_elem[0].get('href', '')
                
                # Extract site source
                site_xpath = './/span[@class="sitestr"]/text()'
                site = story.xpath(site_xpath)
                if site:
                    item['site'] = site[0]
                
                # Get the next sibling row for metadata (points, author, time, comments)
                metadata_row = story.getnext()
                if metadata_row is not None:
                    # Extract points/score
                    score_xpath = './/span[@class="score"]/text()'
                    score = metadata_row.xpath(score_xpath)
                    if score:
                        # Extract number from "291 points"
                        item['points'] = int(score[0].split()[0])
                    
                    # Extract author
                    author_xpath = './/a[@class="hnuser"]/text()'
                    author = metadata_row.xpath(author_xpath)
                    if author:
                        item['author'] = author[0]
                    
                    # Extract time posted
                    time_xpath = './/span[@class="age"]/@title'
                    time_posted = metadata_row.xpath(time_xpath)
                    if time_posted:
                        item['posted_time'] = time_posted[0]
                    
                    # Extract relative time (e.g., "3 hours ago")
                    relative_time_xpath = './/span[@class="age"]/a/text()'
                    relative_time = metadata_row.xpath(relative_time_xpath)
                    if relative_time:
                        item['relative_time'] = relative_time[0]
                    
                    # Extract comment count
                    comments_xpath = './/td[@class="subtext"]//a[contains(text(), "comment")]/text()'
                    comments = metadata_row.xpath(comments_xpath)
                    if comments:
                        # Extract number from "196 comments" or "1 comment"
                        comment_text = comments[0].replace('\xa0', ' ')
                        comment_parts = comment_text.split()
                        if comment_parts:
                            item['comments'] = int(comment_parts[0])
                
                news_items.append(item)
            
            data['news_items'] = news_items
            data['total_items'] = len(news_items)
        
            return data
            
        except Exception as e:
            # If XPath parsing fails, return error information
            return {
                'error': f'Parsing failed: {str(e)}',
                'raw_content_preview': raw_content[:500] if raw_content else 'No content'
            }
