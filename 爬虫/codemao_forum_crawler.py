import requests
import json
import time
import random
import os

def test_post_ids(start_id, end_id, batch_size=20):
    """测试一批帖子ID是否有效"""
    api_url = "https://api.codemao.cn/web/forums/posts/all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://shequ.codemao.cn',
        'Referer': 'https://shequ.codemao.cn/community'
    }
    
    valid_ids = []
    
    # 分批测试ID
    for batch_start in range(start_id, end_id + 1, batch_size):
        batch_end = min(batch_start + batch_size, end_id + 1)
        test_ids = list(range(batch_start, batch_end))
        
        params = {
            'ids': ','.join(map(str, test_ids))
        }
        
        try:
            print(f"\n测试ID范围 {batch_start} - {batch_end-1}...")
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                # 记录有效的帖子ID
                for post in data['items']:
                    valid_ids.append(post['id'])
                print(f"发现 {len(data['items'])} 个有效帖子")
                
                # 保存进度
                save_progress(valid_ids)
            
            # 添加随机延时
            delay = random.uniform(2, 3)
            print(f"等待 {delay:.2f} 秒后继续...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"测试ID时出错: {e}")
            # 如果出错，等待更长时间
            time.sleep(5)
            continue
    
    return valid_ids

def save_progress(valid_ids):
    """保存爬取进度"""
    with open('valid_post_ids.json', 'w', encoding='utf-8') as f:
        json.dump(valid_ids, f, ensure_ascii=False, indent=2)

def load_progress():
    """加载之前的爬取进度"""
    if os.path.exists('valid_post_ids.json'):
        with open('valid_post_ids.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_posts_detail(post_ids):
    """获取帖子详细信息"""
    if not post_ids:
        return []
        
    api_url = "https://api.codemao.cn/web/forums/posts/all"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://shequ.codemao.cn',
        'Referer': 'https://shequ.codemao.cn/community'
    }
    
    # 将ID列表分批处理，每批20个
    all_posts = []
    for i in range(0, len(post_ids), 20):
        batch_ids = post_ids[i:i+20]
        params = {
            'ids': ','.join(map(str, batch_ids))
        }
        
        try:
            print(f"\n正在获取第 {i//20 + 1} 批帖子的详细信息 ({len(batch_ids)} 个)...")
            print(f"请求URL: {api_url}?ids={params['ids']}")
            
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                all_posts.extend(data['items'])
                print(f"成功获取 {len(data['items'])} 个帖子的详细信息")
            else:
                print("API响应格式不符合预期")
            
            # 添加随机延时，避免请求过于频繁
            delay = random.uniform(1, 2)
            print(f"等待 {delay:.2f} 秒后继续...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"获取帖子详情时出错: {e}")
            continue
            
    return all_posts

def format_post(post):
    """格式化帖子信息"""
    user = post.get('user', {})
    reply_user = post.get('reply_user', {})
    comment_user = post.get('comment_user', {})
    
    created_at = time.strftime('%Y-%m-%d %H:%M:%S', 
                              time.localtime(int(post.get('created_at', 0))))
    
    # 处理回复时间
    replied_at = post.get('replied_at', 0)
    if replied_at:
        replied_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(replied_at))
    else:
        replied_at = 'No Reply'
    
    return {
        'title': post.get('title', 'Unknown Title'),
        'author': {
            'nickname': user.get('nickname', 'Unknown Author'),
            'id': user.get('id', 'Unknown ID'),
            'work_shop_name': user.get('work_shop_name', ''),
            'work_shop_level': user.get('work_shop_level', 0)
        },
        'content': post.get('content', '').replace('\n', ' ').strip()[:200] + '...',
        'created_at': created_at,
        'n_replies': post.get('n_replies', 0),
        'n_comments': post.get('n_comments', 0),
        'is_featured': post.get('is_featured', False),
        'is_hotted': post.get('is_hotted', False),
        'is_pinned': post.get('is_pinned', False),
        'last_reply': {
            'user': reply_user.get('nickname', 'No Reply'),
            'time': replied_at
        },
        'last_comment': {
            'user': comment_user.get('nickname', 'No Comment'),
            'time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                time.localtime(post.get('commented_at', 0))) if post.get('commented_at') else 'No Comment'
        }
    }

def save_as_markdown(posts):
    """将帖子信息保存为Markdown文档"""
    filename = f'帖子汇总_{time.strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# 编程猫社区帖子汇总\n\n")
        f.write(f"*生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"*共收集 {len(posts)} 个帖子*\n\n")
        
        # 添加目录
        f.write("## 目录\n\n")
        for i, post in enumerate(posts, 1):
            title = post['title']
            f.write(f"{i}. [{title}](#{i})\n")
        f.write("\n---\n\n")
        
        # 添加帖子详情
        for i, post in enumerate(posts, 1):
            f.write(f"## <span id='{i}'>{i}. {post['title']}</span>\n\n")
            
            # 基本信息
            f.write("### 基本信息\n\n")
            f.write(f"- 作者：{post['author']['nickname']}\n")
            if post['author']['work_shop_name']:
                f.write(f"- 工作室：{post['author']['work_shop_name']} (等级 {post['author']['work_shop_level']})\n")
            f.write(f"- 发布时间：{post['created_at']}\n")
            f.write(f"- 回复数：{post['n_replies']}\n")
            f.write(f"- 评论数：{post['n_comments']}\n")
            
            # 标记
            flags = []
            if post['is_pinned']:
                flags.append("📌置顶")
            if post['is_featured']:
                flags.append("⭐精选")
            if post['is_hotted']:
                flags.append("🔥热门")
            if flags:
                f.write(f"- 标记：{' '.join(flags)}\n")
            
            # 互动信息
            f.write("\n### 互动信息\n\n")
            f.write(f"- 最后回复：{post['last_reply']['user']} 于 {post['last_reply']['time']}\n")
            f.write(f"- 最后评论：{post['last_comment']['user']} 于 {post['last_comment']['time']}\n")
            
            # 内容预览
            f.write("\n### 内容预览\n\n")
            f.write(f"{post['content']}\n\n")
            
            # 分隔线
            f.write("---\n\n")
    
    print(f"\n已生成Markdown文档：{filename}")
    return filename

def main():
    print("开始爬取帖子详细信息...")
    
    # 从valid_post_ids.json加载所有ID
    try:
        with open('valid_post_ids.json', 'r', encoding='utf-8') as f:
            valid_ids = json.load(f)
            print(f"从valid_post_ids.json加载了 {len(valid_ids)} 个帖子ID")
    except Exception as e:
        print(f"加载valid_post_ids.json时出错：{e}")
        return
    
    # 获取帖子详情
    posts = get_posts_detail(valid_ids)
    if not posts:
        print("获取帖子详情失败，停止爬取")
        return
    
    # 处理每个帖子
    all_posts = []
    print(f"\n找到 {len(posts)} 个帖子:")
    for post in posts:
        formatted_post = format_post(post)
        all_posts.append(formatted_post)
        
        print("\n" + "=" * 50)
        print(f"标题: {formatted_post['title']}")
        print(f"作者: {formatted_post['author']['nickname']}")
        if formatted_post['author']['work_shop_name']:
            print(f"工作室: {formatted_post['author']['work_shop_name']} (等级 {formatted_post['author']['work_shop_level']})")
        print(f"发布时间: {formatted_post['created_at']}")
        print(f"回复数: {formatted_post['n_replies']}")
        print(f"评论数: {formatted_post['n_comments']}")
        
        flags = []
        if formatted_post['is_pinned']:
            flags.append("📌置顶")
        if formatted_post['is_featured']:
            flags.append("⭐精选")
        if formatted_post['is_hotted']:
            flags.append("🔥热门")
        if flags:
            print(f"标记: {' '.join(flags)}")
    
    # 保存为JSON文件
    json_filename = f'all_posts_{time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    print(f"\n已保存JSON数据到 {json_filename}")
    
    # 保存为Markdown文档
    md_filename = save_as_markdown(all_posts)
    
    print(f"\n爬取完成，共获取 {len(all_posts)} 个帖子")
    print(f"数据已保存为：")
    print(f"1. JSON文件：{json_filename}")
    print(f"2. Markdown文档：{md_filename}")

if __name__ == "__main__":
    main() 