import { neon } from "@neondatabase/serverless"

export const sql = neon(process.env.DATABASE_URL!)

export interface Meeting {
  id: number
  date: string
  meeting_type: string
  location: string | null
  source_file: string | null
  created_at: string
}

export interface Official {
  id: number
  name: string
  title: string | null
  party: string | null
  district: string | null
  start_date: string | null
  end_date: string | null
}

export interface Vote {
  id: number
  meeting_id: number
  motion_text: string
  motion_number: string | null
  result: string
  yes_count: number
  no_count: number
  abstain_count: number
  absent_count: number
  created_at: string
}

export interface VoteDetail {
  id: number
  vote_id: number
  official_id: number
  vote_cast: string
  official_name?: string
}

export interface OfficialStats {
  id: number
  name: string
  title: string | null
  party: string | null
  total_votes: number
  yes_votes: number
  no_votes: number
  abstentions: number
  absences: number
  attendance_rate: number
}
