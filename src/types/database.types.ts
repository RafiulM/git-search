export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instanciate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.12 (cd3cf9e)"
  }
  public: {
    Tables: {
      documents: {
        Row: {
          content: string
          created_at: string
          description: string | null
          document_type: string
          generated_by: string | null
          generation_prompt: string | null
          id: string
          is_current: boolean | null
          metadata: Json | null
          model_used: string | null
          parent_document_id: string | null
          repository_id: string
          title: string
          updated_at: string
          version: number
        }
        Insert: {
          content: string
          created_at?: string
          description?: string | null
          document_type: string
          generated_by?: string | null
          generation_prompt?: string | null
          id?: string
          is_current?: boolean | null
          metadata?: Json | null
          model_used?: string | null
          parent_document_id?: string | null
          repository_id: string
          title: string
          updated_at?: string
          version?: number
        }
        Update: {
          content?: string
          created_at?: string
          description?: string | null
          document_type?: string
          generated_by?: string | null
          generation_prompt?: string | null
          id?: string
          is_current?: boolean | null
          metadata?: Json | null
          model_used?: string | null
          parent_document_id?: string | null
          repository_id?: string
          title?: string
          updated_at?: string
          version?: number
        }
        Relationships: [
          {
            foreignKeyName: "documents_parent_document_id_fkey"
            columns: ["parent_document_id"]
            isOneToOne: false
            referencedRelation: "documents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "documents_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "documents_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repository_summary"
            referencedColumns: ["id"]
          },
        ]
      }
      repositories: {
        Row: {
          author: string | null
          branch: string | null
          content_expires_at: string | null
          content_url: string | null
          created_at: string
          full_text: string | null
          full_text_path: string | null
          id: string
          name: string
          repo_url: string
          updated_at: string
        }
        Insert: {
          author?: string | null
          branch?: string | null
          content_expires_at?: string | null
          content_url?: string | null
          created_at?: string
          full_text?: string | null
          full_text_path?: string | null
          id?: string
          name: string
          repo_url: string
          updated_at?: string
        }
        Update: {
          author?: string | null
          branch?: string | null
          content_expires_at?: string | null
          content_url?: string | null
          created_at?: string
          full_text?: string | null
          full_text_path?: string | null
          id?: string
          name?: string
          repo_url?: string
          updated_at?: string
        }
        Relationships: []
      }
      repository_analysis: {
        Row: {
          analysis_data: Json | null
          analysis_version: number
          binary_files_skipped: number | null
          created_at: string
          encoding_errors: number | null
          estimated_size_bytes: number | null
          estimated_tokens: number | null
          files_processed: number | null
          id: string
          large_files_skipped: number | null
          repository_id: string
          total_characters: number | null
          total_directories: number | null
          total_files_found: number | null
          total_lines: number | null
          tree_structure: string | null
          updated_at: string
        }
        Insert: {
          analysis_data?: Json | null
          analysis_version?: number
          binary_files_skipped?: number | null
          created_at?: string
          encoding_errors?: number | null
          estimated_size_bytes?: number | null
          estimated_tokens?: number | null
          files_processed?: number | null
          id?: string
          large_files_skipped?: number | null
          repository_id: string
          total_characters?: number | null
          total_directories?: number | null
          total_files_found?: number | null
          total_lines?: number | null
          tree_structure?: string | null
          updated_at?: string
        }
        Update: {
          analysis_data?: Json | null
          analysis_version?: number
          binary_files_skipped?: number | null
          created_at?: string
          encoding_errors?: number | null
          estimated_size_bytes?: number | null
          estimated_tokens?: number | null
          files_processed?: number | null
          id?: string
          large_files_skipped?: number | null
          repository_id?: string
          total_characters?: number | null
          total_directories?: number | null
          total_files_found?: number | null
          total_lines?: number | null
          tree_structure?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "repository_analysis_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "repository_analysis_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repository_summary"
            referencedColumns: ["id"]
          },
        ]
      }
      user_favorites: {
        Row: {
          created_at: string
          id: string
          repository_id: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          repository_id: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          repository_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_favorites_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repositories"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_favorites_repository_id_fkey"
            columns: ["repository_id"]
            isOneToOne: false
            referencedRelation: "repository_summary"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      repository_summary: {
        Row: {
          analysis_created_at: string | null
          analysis_data: Json | null
          author: string | null
          branch: string | null
          created_at: string | null
          estimated_size_bytes: number | null
          estimated_tokens: number | null
          favorite_count: number | null
          files_processed: number | null
          id: string | null
          name: string | null
          repo_url: string | null
          total_characters: number | null
          total_directories: number | null
          total_files_found: number | null
          total_lines: number | null
          tree_structure: string | null
          updated_at: string | null
        }
        Relationships: []
      }
    }
    Functions: {
      get_current_documents: {
        Args: { repo_id: string }
        Returns: {
          content: string
          created_at: string
          description: string | null
          document_type: string
          generated_by: string | null
          generation_prompt: string | null
          id: string
          is_current: boolean | null
          metadata: Json | null
          model_used: string | null
          parent_document_id: string | null
          repository_id: string
          title: string
          updated_at: string
          version: number
        }[]
      }
      get_latest_repository_analysis: {
        Args: { repo_id: string }
        Returns: {
          analysis_data: Json | null
          analysis_version: number
          binary_files_skipped: number | null
          created_at: string
          encoding_errors: number | null
          estimated_size_bytes: number | null
          estimated_tokens: number | null
          files_processed: number | null
          id: string
          large_files_skipped: number | null
          repository_id: string
          total_characters: number | null
          total_directories: number | null
          total_files_found: number | null
          total_lines: number | null
          tree_structure: string | null
          updated_at: string
        }
      }
      get_user_favorite_repositories: {
        Args: { user_id_param: string }
        Returns: {
          author: string | null
          branch: string | null
          content_expires_at: string | null
          content_url: string | null
          created_at: string
          full_text: string | null
          full_text_path: string | null
          id: string
          name: string
          repo_url: string
          updated_at: string
        }[]
      }
      is_favorited_by_user: {
        Args: { repo_id: string; user_id_param: string }
        Returns: boolean
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
