/**
 * WindScope India — API & Pipeline Types
 */

export interface SourceStatus {
  is_operational?: boolean;
  data_source_description?: string;
  last_updated_utc?: string;
  [key: string]: any;
}

export * from './india';
