import config
import requests
import re

headers = {
    "Authorization": "Bearer " + config.NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",  # Check what is the latest version here: https://developers.notion.com/reference/changes-by-version
}


"""
To generate properties with elements and IDs,
execute the code below to retrieve the JSON representation of the existing pages in the database. 
Afterward, you will only need to duplicate the format and update the content accordingly.
"""
def get_pages(num_pages=None):
    url = f"https://api.notion.com/v1/databases/{config.DATABASE_ID}/query"
    get_all = num_pages is None
    page_size = 100 if get_all else num_pages
    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{config.DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    return results

# pages = get_pages()
# for page in pages:
#     page_id = page["id"]
#     props = page["properties"]
#     print(props)

def create_properties(vd_title,author,y_url):
    properties ={

    'Youtuber': {
        'id': 'rMyT',
        'type': 'rich_text',
        'rich_text': [{
            'type': 'text',
            'text': {
                'content': author,
                'link': None
            },
            'annotations': {
                'bold': False,
                'italic': False,
                'strikethrough': False,
                'underline': False,
                'code': False,
                'color': 'default'
            },
            'plain_text': '',
            'href': None
        }]
    },
    'Notion_Page': {
        'id': 'title',
        'type': 'title',
        'title': [{
            'type': 'text',
            'text': {
                'content': vd_title,
                'link': None
            },
            'annotations': {
                'bold': False,
                'italic': False,
                'strikethrough': False,
                'underline': False,
                'code': False,
                'color': 'default'
            },
            'plain_text': '',
            'href': None
        }]
    },
    'URL': {
        'id': 'hCYA',
        'type': 'url',
        'url': y_url
    },
    
    }

    return properties




   
def create_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": config.DATABASE_ID}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)
    if res.status_code == 200:
        print(f"{res.status_code}: Page created successfully")
    else:
        print(f"{res.status_code}: Error during page creation")
    return res


def edit_page(page_block_id, data: dict):
    edit_url = f"https://api.notion.com/v1/blocks/{page_block_id}/children"

    payload = data
    res = requests.patch(edit_url, headers=headers, json=payload)
    if res.status_code == 200:
        print(f"{res.status_code}: Page edited successfully")
    else:
        print(f"{res.status_code}: Error during page editing")
    return res


def extract_blocks(text):
    blocks = []
    pattern = re.compile(r'##\s*(.*?)\s*\n(.*?)(?=\n##|$)', re.DOTALL)

    matches = pattern.finditer(text)
    for match in matches:
        title = match.group(1).strip()
        explanations = [explanation.strip() for explanation in match.group(2).split('*') if explanation.strip()]
        blocks.append({"title": title, "explanations": explanations})

    return blocks


def show_block_properties(result):
    for block in result:
        print(f"Title: {block['title']}")
        print("Explanations:")
        for explanation in block['explanations']:
            print(f"  - {explanation}")
        print()



def format_blocks_as_notion(blocks,youtube_video_url):
    notion_blocks = {
        "children": []
    }
    video_block = {
        "object": "block",
        "type": "video",
        "video": {
            "type": "external",
            "external": {
                "url": youtube_video_url
            }
        }
    }
    notion_blocks["children"].append(video_block)

    for block in blocks:
        title_block = {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": block['title'],
                        },
                    }
                ]
            }
        }
        notion_blocks["children"].append(title_block)

        for explanation in block['explanations']:
            explanation_block = {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": explanation,
                            },
                        }
                    ]
                }
            }
            notion_blocks["children"].append(explanation_block)

    return notion_blocks

def create_item_edit_page(notion_content,title,author,url):

    response = create_page(create_properties(title,author,url))
    page_block_id = response.json()["id"]

    page_properties = extract_blocks(notion_content)


    notion_formatted_blocks = format_blocks_as_notion(page_properties,url)


    edit_page(page_block_id, notion_formatted_blocks)
