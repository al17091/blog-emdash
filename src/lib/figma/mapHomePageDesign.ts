interface HomeDesignInput {
  meta?: {
    title?: string;
  };
  hero?: {
    eyebrow?: string;
    heading?: string;
    description?: string;
    primaryCta?: {
      label?: string;
      href?: string;
    };
    secondaryCta?: {
      label?: string;
      href?: string;
    };
  };
  features?: Array<{
    title?: string;
    description?: string;
  }>;
}

interface HomeDesignOutput {
  hero: {
    eyebrow: string;
    heading: string;
    description: string;
    primaryCta: {
      label: string;
      href: string;
    };
    secondaryCta: {
      label: string;
      href: string;
    };
  };
  features: Array<{
    title: string;
    description: string;
  }>;
}

const defaultOutput: HomeDesignOutput = {
  hero: {
    eyebrow: 'Design System Sync',
    heading: 'Figma MCP connected Astro page',
    description: 'Update JSON from Figma MCP output to refresh this page quickly.',
    primaryCta: {
      label: 'Get started',
      href: '#',
    },
    secondaryCta: {
      label: 'View docs',
      href: '#',
    },
  },
  features: [
    {
      title: 'Structured import',
      description: 'Map Figma nodes to Astro component props.',
    },
    {
      title: 'Token-first styling',
      description: 'Keep color and spacing in one place for consistency.',
    },
    {
      title: 'Composable sections',
      description: 'Break sections into components for long-term maintenance.',
    },
  ],
};

export function mapHomePageDesign(input: HomeDesignInput): HomeDesignOutput {
  return {
    hero: {
      eyebrow: input.hero?.eyebrow ?? defaultOutput.hero.eyebrow,
      heading: input.hero?.heading ?? defaultOutput.hero.heading,
      description: input.hero?.description ?? defaultOutput.hero.description,
      primaryCta: {
        label: input.hero?.primaryCta?.label ?? defaultOutput.hero.primaryCta.label,
        href: input.hero?.primaryCta?.href ?? defaultOutput.hero.primaryCta.href,
      },
      secondaryCta: {
        label: input.hero?.secondaryCta?.label ?? defaultOutput.hero.secondaryCta.label,
        href: input.hero?.secondaryCta?.href ?? defaultOutput.hero.secondaryCta.href,
      },
    },
    features:
      input.features
        ?.filter((item) => item.title && item.description)
        .map((item) => ({
          title: item.title as string,
          description: item.description as string,
        })) ?? defaultOutput.features,
  };
}
