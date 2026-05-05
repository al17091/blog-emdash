import { defineCollection, z } from 'astro:content';

const jstDateTimePattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/;
const localImagePathPattern = /^\/images\/blog\/.+/;

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['tech', 'nature', 'travel']),
    routeSlug: z.string(),
    author: z.string(),
    publishedDate: z
      .string()
      .regex(jstDateTimePattern, 'Use YYYY-MM-DDTHH:mm:ss (JST local time)')
      .transform((value) => new Date(`${value}+09:00`)),
    readTime: z.string(),
    cardImage: z.string().regex(localImagePathPattern, 'Use local path like /images/blog/...'),
    heroImage: z.string().regex(localImagePathPattern, 'Use local path like /images/blog/...').optional(),
    tags: z.array(z.string()),
    navLabel: z.string(),
    sortOrder: z.number(),
    related: z.array(z.string()).default([]),
  }),
});

export const collections = { blog };
