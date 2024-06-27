import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_root_layout/')({
  component: () => <div>Hello /!</div>
})