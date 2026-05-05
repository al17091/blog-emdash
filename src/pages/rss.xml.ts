import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context: { site?: URL }) {
  const posts = (await getCollection('blog')).sort(
    (a, b) => b.data.publishedDate.getTime() - a.data.publishedDate.getTime(),
  );

  return rss({
    title: 'Multi-Theme Blog',
    description: 'Engineering, nature, and travel stories.',
    site: context.site ?? new URL('http://localhost:4321'),
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.publishedDate,
      link: `/blog/${post.data.category}/${post.data.routeSlug}`,
    })),
  });
}
