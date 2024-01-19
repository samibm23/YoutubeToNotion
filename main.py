from summarize import extract_youtube
from notion_database import create_item_edit_page

def main():
    video_url = input("Enter a youtube video URL: ")
    
    yn_data = extract_youtube(video_url)
    create_item_edit_page(yn_data["notion_page"],yn_data["title"],yn_data["author"],video_url)

if __name__ == "__main__":
    main()