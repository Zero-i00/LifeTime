import { TestLinkData } from '@/features/link/data/test.data'
import DiffView from '@/features/link/views/DiffView'

export default function Home() {
  return (
    <main>
        <section className="mx-auto max-w-180 mt-52">
          <DiffView
            schema={TestLinkData.schema}
              different={TestLinkData.different}
          />
        </section>
      </main>
  );
}
