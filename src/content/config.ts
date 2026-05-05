import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['tech', 'nature', 'travel']),
    routeSlug: z.string(),
    author: z.string(),
    publishedDate: z.string(),
    readTime: z.string(),
    cardImage: z.string().url(),
    heroImage: z.string().url(),
    tags: z.array(z.string()),
    navLabel: z.string(),
    sortOrder: z.number(),
    related: z.array(z.string()).default([]),
  }),
});

export const collections = { blog };
