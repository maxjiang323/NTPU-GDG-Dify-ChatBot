
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const linkVariants = cva(
  "inline-flex items-center text-primary underline-offset-4 hover:underline",
  {
    variants: {
      variant: {
        default: "",
        muted: "text-muted-foreground hover:text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface LinkProps
  extends React.AnchorHTMLAttributes<HTMLAnchorElement>,
    VariantProps<typeof linkVariants> {
  asChild?: boolean
}

const Link = React.forwardRef<HTMLAnchorElement, LinkProps>(
  ({ className, variant, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "a"
    return (
      <Comp
        className={cn(linkVariants({ variant, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Link.displayName = "Link"

export { Link, linkVariants }
