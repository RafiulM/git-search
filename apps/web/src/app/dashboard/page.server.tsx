import { getRepositoryStatistics } from '@/lib/api';
import DashboardClient from './page.client';

export default async function DashboardPage() {
  try {
    // Fetch global statistics
    const stats = await getRepositoryStatistics();

    return <DashboardClient stats={stats} />;
  } catch (error) {
    console.error('Failed to fetch dashboard statistics:', error);
    return <DashboardClient stats={null} />;
  }
}