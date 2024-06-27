import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_root_layout/about')({
  component: () => <div>Hello /about!</div>
})