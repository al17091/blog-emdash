export type BlogCategory = 'tech' | 'nature' | 'travel';

export interface RelatedArticle {
  title: string;
  categoryLabel: string;
  date: string;
  readTime: string;
  image: string;
  href: string;
}

export interface ArticleRecord {
  category: BlogCategory;
  slug: string;
  brand: string;
  navItems: string[];
  breadcrumb: string[];
  title: string;
  description: string;
  author: string;
  publishedDate: string;
  heroImage: string;
  heroCaption: string;
  intro: string[];
  sectionHeading: string;
  sectionBody: string[];
  quote: {
    text: string;
    source: string;
  };
  bulletHeading: string;
  bullets: string[];
  codeHeading: string;
  codeLead: string;
  codeBlock: string;
  diagramHeading: string;
  diagramCaption: string;
  bestPracticesHeading: string;
  bestPractices: string[];
  related: RelatedArticle[];
}

export const articles: ArticleRecord[] = [
  {
    category: 'tech',
    slug: 'scaling-microservices-cloud-native-architecture',
    brand: 'I am Engineer',
    navItems: ['Articles', 'Tutorials', 'Architecture', 'Cloud'],
    breadcrumb: ['Portal', 'Tech Blog', 'Scaling Microservices'],
    title: 'Scaling Microservices with Cloud-Native Architecture',
    description:
      'A deep dive into resilient system design, service meshes, and implementation strategies for modern high-traffic applications.',
    author: 'Alex Chen',
    publishedDate: 'Oct 24, 2023',
    heroImage: 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=1600&q=80',
    heroCaption: 'Conceptualizing distributed cloud architecture in modern enterprise environments.',
    intro: [
      'Microservices have revolutionized the way we build and deploy software. However, as systems grow in complexity, managing the communication, reliability, and observability between these services becomes a monumental task.',
      'Cloud-native architecture provides a practical framework to address these challenges through containerization, orchestration, and managed services.',
    ],
    sectionHeading: 'The Challenge of Scale',
    sectionBody: [
      'Scaling is not just about adding more instances. It is about ensuring your system can handle increased load without compromising on latency or availability.',
      'In a microservices environment, this often means addressing the network tax and implementing robust failure mechanisms.',
    ],
    quote: {
      text: 'The first rule of distributed systems is dont distribute. But when you must, do it with the clarity of a unified architectural vision.',
      source: 'System Design Principle, 2023',
    },
    bulletHeading: 'Core Components for Scaling',
    bullets: [
      'Service Discovery: Automatically detect services on a network as they come and go.',
      'Load Balancing: Distribute incoming traffic across multiple instances to optimize resource use.',
      'Circuit Breaking: Prevent cascading failures by stopping calls to failing services.',
      'Sidecar Patterns: Offload common tasks like logging and monitoring to a separate process.',
    ],
    codeHeading: 'Implementing Auto-scaling',
    codeLead:
      'A typical Kubernetes configuration for horizontal pod autoscaling might look like this snippet below. It ensures your services remain responsive during traffic spikes.',
    codeBlock: `apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: microservice-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: microservice-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70`,
    diagramHeading: 'Architectural Blueprint',
    diagramCaption: 'Logical illustration: Dynamic routing and load balancing workflow between ingress controllers and service mesh sidecars.',
    bestPracticesHeading: 'Best Practices',
    bestPractices: [
      'Prioritize stateless services for easier horizontal scaling.',
      'Implement centralized logging and distributed tracing.',
      'Use asynchronous communication for non-critical path operations.',
      'Test your resilience with chaos engineering tools.',
    ],
    related: [
      {
        title: 'Serverless Patterns for High Availability',
        categoryLabel: 'Cloud Architecture',
        date: 'Nov 7, 2023',
        readTime: '8 min read',
        image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
        href: '/blog/tech/cherry-blossoms-kyoto',
      },
      {
        title: 'Mastering Go for Concurrent Systems',
        categoryLabel: 'Software Engineering',
        date: 'Oct 26, 2023',
        readTime: '15 min read',
        image: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=900&q=80',
        href: '/blog/tech/street-food-bangkok',
      },
      {
        title: 'Zero Trust Networking in Practice',
        categoryLabel: 'Security',
        date: 'Oct 15, 2023',
        readTime: '10 min read',
        image: 'https://images.unsplash.com/photo-1563206767-5b18f218e8de?auto=format&fit=crop&w=900&q=80',
        href: '/blog/tech/swiss-alps-retreat',
      },
    ],
  },
  {
    category: 'nature',
    slug: 'first-ascent-mount-tsurugi',
    brand: '素人登山道',
    navItems: ['Climb Records', 'Gear Reviews', 'Trail Lessons', 'About'],
    breadcrumb: ['Portal', 'Nature', 'First Ascent'],
    title: 'First Ascent of Mount Tsurugi: A Humbling Traverse',
    description:
      'A personal log from a long ridge route, including weather shifts, pacing decisions, and the quiet discipline of descending safely.',
    author: 'Nao Hiker',
    publishedDate: 'Oct 24, 2023',
    heroImage: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80',
    heroCaption: 'Morning ridgeline before the clouds closed in over the northern slope.',
    intro: [
      'The route began calmly, with a steady incline through mixed forest and clear visibility across the valley floor.',
      'By midday, winds intensified and forced us to shorten rest stops. The climb became less about speed and more about controlled breathing and step economy.',
    ],
    sectionHeading: 'Managing Pace on Long Ridges',
    sectionBody: [
      'Early pacing determines your descent quality. If you overspend energy in the first half, technical sections become risk points later.',
      'We used a simple rhythm: thirty-five minutes of movement, five minutes of hydration and pack check.',
    ],
    quote: {
      text: 'Summits reward patience, but descents demand humility.',
      source: 'Field Notes, Autumn Traverse',
    },
    bulletHeading: 'Trail Lessons from This Route',
    bullets: [
      'Preload GPX and paper map as backup before entering low-signal zones.',
      'Keep one dry base layer for ridge breaks to avoid rapid cooling.',
      'Use trekking poles proactively on loose rock, not only when tired.',
      'Commit to turnaround times before conditions become ambiguous.',
    ],
    codeHeading: 'Lightweight Pack Checklist',
    codeLead: 'This packing format helped keep weight under control without sacrificing safety essentials.',
    codeBlock: `Essentials:
- shell jacket (waterproof)
- thermal layer
- 1.5L water + filter
- headlamp + backup battery

Navigation:
- offline map app
- printed route map
- compass

Safety:
- first aid kit
- emergency bivy
- whistle`,
    diagramHeading: 'Route Snapshot',
    diagramCaption: 'Elevation profile summary and waypoint markers for ascent and descent flow.',
    bestPracticesHeading: 'What Worked Well',
    bestPractices: [
      'Set hard weather checkpoints before committing to exposed ridges.',
      'Pair nutrition with elevation milestones to avoid energy crashes.',
      'Capture route notes immediately after descent while details are fresh.',
      'Treat descent as a separate phase with its own pacing plan.',
    ],
    related: [
      {
        title: 'Mirror Lakes of Kamikochi',
        categoryLabel: 'Nature',
        date: 'Sep 15, 2023',
        readTime: '7 min read',
        image: 'https://images.unsplash.com/photo-1439853949127-fa647821eba0?auto=format&fit=crop&w=900&q=80',
        href: '/blog/nature/mirror-lakes-kamikochi',
      },
      {
        title: 'Lightweight Packing: The 5kg Challenge',
        categoryLabel: 'Gear Review',
        date: 'Sep 28, 2023',
        readTime: '14 min read',
        image: 'https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=900&q=80',
        href: '/blog/nature/lightweight-packing-5kg',
      },
      {
        title: 'Mountain Hut Etiquette',
        categoryLabel: 'Trail Lessons',
        date: 'Sep 2, 2023',
        readTime: '11 min read',
        image: 'https://images.unsplash.com/photo-1508061253366-f7da158b6d46?auto=format&fit=crop&w=900&q=80',
        href: '/blog/nature/mountain-hut-etiquette',
      },
    ],
  },
  {
    category: 'travel',
    slug: 'sunrise-ferry-naoshima',
    brand: 'フリーダム旅行記',
    navItems: ['Journal', 'Routes', 'Food', 'About'],
    breadcrumb: ['Portal', 'Travel Log', 'Naoshima Ferry'],
    title: 'Sunrise Ferry to Naoshima: A Slow Start Worth Waking Up For',
    description:
      'A practical morning route across the Seto Inland Sea, including departure timing, onboard tips, and a no-rush island walking plan.',
    author: 'Mio Traveler',
    publishedDate: 'Nov 3, 2023',
    heroImage: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80',
    heroCaption: 'First light over the harbor before boarding the early ferry.',
    intro: [
      'Catching the first ferry changed the rhythm of the entire day. Streets were quiet, and the port felt more like a neighborhood than a transit point.',
      'The crossing itself was short, but the reduced crowd made every transfer smoother once we arrived.',
    ],
    sectionHeading: 'Timing and Transfers',
    sectionBody: [
      'Give yourself at least twenty minutes at the terminal if you are carrying luggage. Ticket queues are short in the early morning but can still bottleneck at boarding gates.',
      'Once on the island, start with a walkable cluster of stops before relying on buses. It keeps your plan resilient when schedules shift.',
    ],
    quote: {
      text: 'Good travel days are rarely fast. They are simply well-paced.',
      source: 'Port Journal Notes',
    },
    bulletHeading: 'Small Things That Helped',
    bullets: [
      'Pack coins and a transit card before leaving the city.',
      'Carry a light wind layer; deck air is cooler than expected.',
      'Book one anchor meal and leave the rest flexible.',
      'Map two backup cafes near your final return ferry.',
    ],
    codeHeading: 'One-day Route Draft',
    codeLead: 'A compact itinerary that leaves buffer for weather and photo stops.',
    codeBlock: `07:10 Depart Uno Port
07:35 Arrive Miyanoura
08:00 Breakfast + coffee
09:00 Coastal walk and galleries
12:30 Lunch near Honmura
15:00 Museum block
17:20 Return ferry`,
    diagramHeading: 'Route Blueprint',
    diagramCaption: 'Harbor arrival, walkable clusters, and afternoon museum window.',
    bestPracticesHeading: 'Travel Ops Notes',
    bestPractices: [
      'Anchor the day with fixed departures, not fixed attractions.',
      'Prioritize walkable loops to reduce transfer friction.',
      'Store key addresses in offline maps before boarding.',
      'End with a short review note for your next trip iteration.',
    ],
    related: [
      {
        title: '48 Hours in Taipei',
        categoryLabel: 'City Guide',
        date: 'Oct 28, 2023',
        readTime: '6 min read',
        image: 'https://images.unsplash.com/photo-1470004914212-05527e49370b?auto=format&fit=crop&w=900&q=80',
        href: '/blog/travel/48-hours-in-taipei',
      },
      {
        title: 'Weekend in Kanazawa',
        categoryLabel: 'Culture',
        date: 'Oct 6, 2023',
        readTime: '6 min read',
        image: 'https://images.unsplash.com/photo-1492571350019-22de08371fd3?auto=format&fit=crop&w=900&q=80',
        href: '/blog/travel/weekend-in-kanazawa',
      },
      {
        title: 'Packing Light for 10 Days',
        categoryLabel: 'Tips',
        date: 'Sep 24, 2023',
        readTime: '4 min read',
        image: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=900&q=80',
        href: '/blog/travel/packing-light-10-days',
      },
    ],
  },
];

export function getArticle(category: string, slug: string): ArticleRecord | undefined {
  return articles.find((article) => article.category === category && article.slug === slug);
}

export interface BlogPostCard {
  slug: string;
  title: string;
  description: string;
  date: string;
  readTime: string;
  author: string;
  image: string;
  tags: string[];
}

export const categoryPosts: Record<BlogCategory, BlogPostCard[]> = {
  tech: [
    {
      slug: 'scaling-microservices-cloud-native-architecture',
      title: 'Scaling Microservices with Cloud-Native Architecture',
      description:
        'A deep dive into resilient system design, service meshes, and implementation strategies for modern high-traffic applications.',
      date: 'Oct 24, 2023',
      readTime: '5 MIN READ',
      author: 'Alex Chen',
      image: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=900&q=80',
      tags: ['Astro', 'GitOps'],
    },
    {
      slug: 'cherry-blossoms-kyoto',
      title: 'Cherry Blossoms in Kyoto',
      description: 'A guide to the most scenic spots during sakura season and the best routes to walk.',
      date: 'Oct 20, 2023',
      readTime: '8 MIN READ',
      author: 'Yuki Sato',
      image: 'https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=900&q=80',
      tags: ['Season'],
    },
    {
      slug: 'street-food-bangkok',
      title: 'Street Food of Bangkok',
      description: 'Discovering the spicy and sweet flavors of the night market and local hidden stalls.',
      date: 'Oct 15, 2023',
      readTime: '6 MIN READ',
      author: 'Sam Eats',
      image: 'https://images.unsplash.com/photo-1569058242567-93de6f36f8eb?auto=format&fit=crop&w=900&q=80',
      tags: ['Food', 'Hot'],
    },
    {
      slug: 'swiss-alps-retreat',
      title: 'The Swiss Alps Retreat',
      description: 'Hiking through the snow-capped peaks of Switzerland with practical packing tips.',
      date: 'Oct 10, 2023',
      readTime: '12 MIN READ',
      author: 'Clara Alp',
      image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=80',
      tags: ['Adventure'],
    },
    {
      slug: 'sunset-santorini',
      title: 'Sunset in Santorini',
      description: "Finding the perfect spot for the world's most famous sunset and avoiding crowds.",
      date: 'Oct 05, 2023',
      readTime: '7 MIN READ',
      author: 'Elena Sun',
      image: 'https://images.unsplash.com/photo-1469796466635-455ede028aca?auto=format&fit=crop&w=900&q=80',
      tags: ['Europe'],
    },
    {
      slug: 'hidden-cafes-paris',
      title: 'Hidden Cafes in Paris',
      description: 'Exploring the quiet corners and best croissants of the 10th arrondissement.',
      date: 'Oct 01, 2023',
      readTime: '4 MIN READ',
      author: 'Jean Roux',
      image: 'https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=900&q=80',
      tags: ['City'],
    },
    {
      slug: 'icelandic-road-trip',
      title: 'Icelandic Road Trip',
      description: 'A complete guide to driving the Ring Road, from waterfalls to black sand beaches.',
      date: 'Sep 28, 2023',
      readTime: '15 MIN READ',
      author: 'Erik Frost',
      image: 'https://images.unsplash.com/photo-1504893524553-b855bce32c67?auto=format&fit=crop&w=900&q=80',
      tags: ['Road'],
    },
    {
      slug: 'market-day-marrakesh',
      title: 'Market Day in Marrakesh',
      description: 'The colors and scents of the ancient medina. Finding treasure in local souks.',
      date: 'Sep 22, 2023',
      readTime: '10 MIN READ',
      author: 'Nora Souk',
      image: 'https://images.unsplash.com/photo-1597764699512-fd04de4e6908?auto=format&fit=crop&w=900&q=80',
      tags: ['Culture'],
    },
    {
      slug: 'seoul-night-life',
      title: 'Seoul Night Life',
      description: 'Best places for late night snacks and neon light photography in Seoul.',
      date: 'Sep 18, 2023',
      readTime: '9 MIN READ',
      author: 'Jiwon Kim',
      image: 'https://images.unsplash.com/photo-1538485399081-7c8978ec8f85?auto=format&fit=crop&w=900&q=80',
      tags: ['City'],
    },
    {
      slug: 'great-barrier-reef',
      title: 'The Great Barrier Reef',
      description: "Diving into the world's largest coral reef system in Australia with safety essentials.",
      date: 'Sep 12, 2023',
      readTime: '11 MIN READ',
      author: 'Dave Dive',
      image: 'https://images.unsplash.com/photo-1544551763-77ef2d0cfc6c?auto=format&fit=crop&w=900&q=80',
      tags: ['Nature'],
    },
    {
      slug: 'rustic-pasta-rome',
      title: 'Rustic Pasta in Rome',
      description: 'Authentic carbonara in the heart of the eternal city with neighborhood picks.',
      date: 'Sep 08, 2023',
      readTime: '5 MIN READ',
      author: 'Maria Gusto',
      image: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=900&q=80',
      tags: ['Food'],
    },
    {
      slug: 'hokkaido-winter-wonders',
      title: 'Hokkaido Winter Wonders',
      description: 'Exploring the seafood and snow festivals of the north during peak winter.',
      date: 'Sep 02, 2023',
      readTime: '14 MIN READ',
      author: 'Hiro Snow',
      image: 'https://images.unsplash.com/photo-1482192505345-5655af888cc4?auto=format&fit=crop&w=900&q=80',
      tags: ['Winter'],
    },
  ],
  nature: [
    {
      slug: 'first-ascent-mount-tsurugi',
      title: 'First Ascent of Mount Tsurugi: A Humbling Traverse',
      description: 'The climb was steep, and my breath was short, but the silence at the summit taught me more than any guidebook.',
      date: 'Oct 24, 2023',
      readTime: '12 min read',
      author: 'Nao Hiker',
      image: 'https://images.unsplash.com/photo-1464822759844-d150ad6d1d07?auto=format&fit=crop&w=1000&q=80',
      tags: ['CLIMB RECORD'],
    },
    {
      slug: 'essential-boots-rocky-terrain',
      title: 'Essential Boots for Rocky Terrain: A 100km Test',
      description: 'After traversing the North Alps, I finally found the limit of these boots. Here is why durability matters.',
      date: 'Oct 20, 2023',
      readTime: '8 min read',
      author: 'Gear Scout',
      image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1000&q=80',
      tags: ['GEAR REVIEW'],
    },
    {
      slug: 'zen-of-the-descent',
      title: 'The Zen of the Descent: Finding Focus When Tired',
      description: 'While reaching the top is the goal, the way back down is where the true mental training begins.',
      date: 'Oct 15, 2023',
      readTime: '15 min read',
      author: 'Trail Mentor',
      image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1000&q=80',
      tags: ['TRAIL LESSONS'],
    },
    {
      slug: 'under-the-stars-hotaka',
      title: 'Under the Stars: A Solo Night on Mount Hotaka',
      description: 'Nothing prepares you for the absolute solitude of a mountain ridge at midnight. A journey of quiet grit.',
      date: 'Oct 10, 2023',
      readTime: '20 min read',
      author: 'Night Walker',
      image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=80',
      tags: ['CLIMB RECORD'],
    },
    {
      slug: 'listening-to-the-wind',
      title: 'Listening to the Wind: Why I Hike Alone',
      description: 'Solo hiking is not about being lonely, it is about being present. How the sounds of nature sharpen judgment.',
      date: 'Oct 05, 2023',
      readTime: '10 min read',
      author: 'Forest Echo',
      image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80',
      tags: ['TRAIL LESSONS'],
    },
    {
      slug: 'lightweight-packing-5kg',
      title: 'Lightweight Packing: The 5kg Challenge',
      description: 'Can you really do a 3-day hike with only 5kg? Here is the ultralight kit that changed how I move.',
      date: 'Sep 28, 2023',
      readTime: '14 min read',
      author: 'Pack Light',
      image: 'https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=1000&q=80',
      tags: ['GEAR REVIEW'],
    },
    {
      slug: 'mirror-lakes-kamikochi',
      title: 'Mirror Lakes of Kamikochi',
      description: 'A gentle trail for those who want to see the beauty of the Alps without the extreme exertion.',
      date: 'Sep 15, 2023',
      readTime: '7 min read',
      author: 'Alpine View',
      image: 'https://images.unsplash.com/photo-1439853949127-fa647821eba0?auto=format&fit=crop&w=1000&q=80',
      tags: ['CLIMB RECORD'],
    },
    {
      slug: 'mountain-hut-etiquette',
      title: "Mountain Hut Etiquette: A Respectful Hiker's Guide",
      description: 'Sharing a small space with dozens of strangers requires a specific set of unwritten rules.',
      date: 'Sep 02, 2023',
      readTime: '11 min read',
      author: 'Cabin Note',
      image: 'https://images.unsplash.com/photo-1508061253366-f7da158b6d46?auto=format&fit=crop&w=1000&q=80',
      tags: ['TRAIL LESSONS'],
    },
  ],
  travel: [
    {
      slug: 'sunrise-ferry-naoshima',
      title: 'Sunrise Ferry to Naoshima',
      description: 'Early departure, calm water, and a quiet art island waking up. A practical log for first-time visitors.',
      date: 'Nov 03, 2023',
      readTime: '7 MIN READ',
      author: 'Mio Traveler',
      image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80',
      tags: ['Island', 'Japan'],
    },
    {
      slug: '48-hours-in-taipei',
      title: '48 Hours in Taipei',
      description: 'Night markets, local coffee, and a compact route that covers food, design spots, and city walks.',
      date: 'Oct 28, 2023',
      readTime: '6 MIN READ',
      author: 'Ren Nomad',
      image: 'https://images.unsplash.com/photo-1470004914212-05527e49370b?auto=format&fit=crop&w=900&q=80',
      tags: ['City'],
    },
    {
      slug: 'train-window-notes-hokkaido',
      title: 'Train Window Notes from Hokkaido',
      description: 'A winter rail route with station-by-station notes, warm stops, and realistic transfer times.',
      date: 'Oct 21, 2023',
      readTime: '9 MIN READ',
      author: 'Aki Rail',
      image: 'https://images.unsplash.com/photo-1519183071298-a2962be96f83?auto=format&fit=crop&w=900&q=80',
      tags: ['Rail', 'Winter'],
    },
    {
      slug: 'lisbon-on-foot',
      title: 'Lisbon on Foot: 12km Loop',
      description: 'A steep but rewarding loop through miradouros, old trams, and less crowded dinner spots.',
      date: 'Oct 16, 2023',
      readTime: '8 MIN READ',
      author: 'Clara Steps',
      image: 'https://images.unsplash.com/photo-1513735492246-483525079686?auto=format&fit=crop&w=900&q=80',
      tags: ['Europe'],
    },
    {
      slug: 'morning-market-chiang-mai',
      title: 'Morning Market in Chiang Mai',
      description: 'What to eat first, how much to budget, and where to find quieter lanes before noon.',
      date: 'Oct 11, 2023',
      readTime: '5 MIN READ',
      author: 'Pim Foodie',
      image: 'https://images.unsplash.com/photo-1528181304800-259b08848526?auto=format&fit=crop&w=900&q=80',
      tags: ['Food'],
    },
    {
      slug: 'weekend-in-kanazawa',
      title: 'Weekend in Kanazawa',
      description: 'Craft streets, calm gardens, and a low-stress route that works well without a car.',
      date: 'Oct 06, 2023',
      readTime: '6 MIN READ',
      author: 'Nao Guide',
      image: 'https://images.unsplash.com/photo-1492571350019-22de08371fd3?auto=format&fit=crop&w=900&q=80',
      tags: ['Culture'],
    },
    {
      slug: 'bus-route-across-patagonia',
      title: 'Bus Route Across Patagonia',
      description: 'Cross-border timing, ticket cautions, and where to break up long rides without losing daylight.',
      date: 'Sep 30, 2023',
      readTime: '11 MIN READ',
      author: 'Leo South',
      image: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=900&q=80',
      tags: ['Long Trip'],
    },
    {
      slug: 'packing-light-10-days',
      title: 'Packing Light for 10 Days',
      description: 'A tested carry-on setup with climate layering and a simple laundry rhythm that actually works.',
      date: 'Sep 24, 2023',
      readTime: '4 MIN READ',
      author: 'Yuna Pack',
      image: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=900&q=80',
      tags: ['Tips'],
    },
  ],
};

export function getPostCard(category: string, slug: string): BlogPostCard | undefined {
  const key = category as BlogCategory;
  return categoryPosts[key]?.find((post) => post.slug === slug);
}

export function getAllArticleParams(): Array<{ category: BlogCategory; slug: string }> {
  return (Object.keys(categoryPosts) as BlogCategory[]).flatMap((category) =>
    categoryPosts[category].map((post) => ({ category, slug: post.slug })),
  );
}

export function getArticleOrDefault(category: string, slug: string): ArticleRecord | undefined {
  const explicit = getArticle(category, slug);
  if (explicit) return explicit;

  const post = getPostCard(category, slug);
  if (!post) return undefined;

  const cat = category as BlogCategory;
  const defaults = {
    tech: {
      brand: 'I am Engineer',
      navItems: ['Articles', 'Tutorials', 'Architecture', 'Cloud'],
      breadcrumb: ['Portal', 'Tech Blog', post.title],
      sectionHeading: 'Implementation Notes',
      quote: 'Well-structured systems age better than fast patches.',
      source: 'Engineering Journal',
      bulletHeading: 'Takeaways',
      codeHeading: 'Reference Snippet',
      codeBlock: 'const plan = { reliability: true, observability: true, scale: true };',
      diagramHeading: 'Architecture Snapshot',
      diagramCaption: 'Service boundaries and communication flow for this topic.',
      bestPracticesHeading: 'Practical Checklist',
    },
    nature: {
      brand: '素人登山道',
      navItems: ['Climb Records', 'Gear Reviews', 'Trail Lessons', 'About'],
      breadcrumb: ['Portal', 'Nature', post.title],
      sectionHeading: 'Trail Context',
      quote: 'Pacing is safety in another form.',
      source: 'Mountain Field Notes',
      bulletHeading: 'Lessons Learned',
      codeHeading: 'Field Checklist',
      codeBlock: '- weather check\n- route backup\n- hydration plan\n- descent timing',
      diagramHeading: 'Route Blueprint',
      diagramCaption: 'Waypoint and elevation flow captured from the route log.',
      bestPracticesHeading: 'What To Repeat',
    },
    travel: {
      brand: 'フリーダム旅行記',
      navItems: ['Journal', 'Routes', 'Food', 'About'],
      breadcrumb: ['Portal', 'Travel Log', post.title],
      sectionHeading: 'Route Notes',
      quote: 'Good travel feels light because the plan is simple.',
      source: 'Travel Desk Memo',
      bulletHeading: 'Useful Tips',
      codeHeading: 'Itinerary Draft',
      codeBlock: '08:00 start\n11:00 local stop\n14:00 transfer\n18:00 return',
      diagramHeading: 'Trip Outline',
      diagramCaption: 'Core route with optional stops for weather or timing shifts.',
      bestPracticesHeading: 'Next Time Improvements',
    },
  }[cat];

  const related = categoryPosts[cat]
    .filter((item) => item.slug !== slug)
    .slice(0, 3)
    .map((item) => ({
      title: item.title,
      categoryLabel: item.tags[0] ?? cat.toUpperCase(),
      date: item.date,
      readTime: item.readTime,
      image: item.image,
      href: `/blog/${cat}/${item.slug}`,
    }));

  return {
    category: cat,
    slug: post.slug,
    brand: defaults.brand,
    navItems: defaults.navItems,
    breadcrumb: defaults.breadcrumb,
    title: post.title,
    description: post.description,
    author: post.author,
    publishedDate: post.date,
    heroImage: post.image,
    heroCaption: post.description,
    intro: [
      `${post.title} is part of the ${cat} archive and follows the same editorial format across this blog.`,
      post.description,
    ],
    sectionHeading: defaults.sectionHeading,
    sectionBody: [
      'This entry captures context, constraints, and actionable notes in a structure optimized for fast rereads.',
      'The goal is to keep each article clear enough to be reused as a reference in future planning.',
    ],
    quote: {
      text: defaults.quote,
      source: defaults.source,
    },
    bulletHeading: defaults.bulletHeading,
    bullets: [
      'Summarize key constraints first.',
      'Separate observations from decisions.',
      'Keep the next action explicit.',
      'Record one thing to improve next time.',
    ],
    codeHeading: defaults.codeHeading,
    codeLead: 'This compact block shows a reusable structure for documenting the workflow.',
    codeBlock: defaults.codeBlock,
    diagramHeading: defaults.diagramHeading,
    diagramCaption: defaults.diagramCaption,
    bestPracticesHeading: defaults.bestPracticesHeading,
    bestPractices: [
      'Write for future-you first.',
      'Keep references discoverable by slug.',
      'Use consistent sections across categories.',
      'Prefer clarity over verbosity.',
    ],
    related,
  };
}
