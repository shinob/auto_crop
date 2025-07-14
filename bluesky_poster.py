#!/usr/bin/env python3  

import argparse
import sys
from atproto import Client, models
from atproto_client.models.app.bsky.embed.defs import AspectRatio
import config

from PIL import Image
import io


def post_image_to_bluesky(image_path: str, post_text: str):
    """
    Posts an image with accompanying text to Bluesky.

    Args:
        image_path (str): The path to the image file.
        post_text (str): The text content for the post.
    """
    client = Client(base_url='https://bsky.social')
    client.login(config.BLUESKY_HANDLE, config.BLUESKY_APP_PASSWORD)

    with open(image_path, 'rb') as f:
        img_data = f.read()
    
    #upload = client.com.atproto.repo.upload_blob(img_data)
    #images = [models.AppBskyEmbedImages.Image(alt=post_text, image=upload.blob)]
    #embed = models.AppBskyEmbedImages.Main(images=images)
        
    # 画像サイズを取得
    with Image.open(io.BytesIO(img_data)) as img:
        img_width, img_height = img.size
    
    # aspect_ratio を指定
    ar = AspectRatio(width=img_width, height=img_height)

    upload = client.com.atproto.repo.upload_blob(img_data)
    image = models.AppBskyEmbedImages.Image(alt=post_text, image=upload.blob, aspect_ratio=ar)
    embed = models.AppBskyEmbedImages.Main(images=[image])

    client.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client.me.did,
            collection=models.ids.AppBskyFeedPost,
            record=models.AppBskyFeedPost.Record(
                text=post_text,
                embed=embed,
                created_at=client.get_current_time_iso(),
            ),
        )
    )

    print("Successfully posted to Bluesky!")

def main():
    parser = argparse.ArgumentParser(description='Post an image to Bluesky.')
    parser.add_argument('image_path', type=str, help='The path to the image to post.')
    parser.add_argument('post_text', type=str, help='The text to accompany the image.')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    post_image_to_bluesky(args.image_path, args.post_text)

if __name__ == '__main__':
    main()