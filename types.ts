
export interface Track {
  name: string;
  id: string;
  uri: string;
  popularity: number;
  preview_url?: string;
}

export interface Artist {
  id?: string;
  name: string;
  imageUrl?: string;
  image?: string;
  topSongs?: string[];
  top_tracks?: string[];
  track_details?: Track[];
  popularity?: number;
}

export interface MusicSectionData {
  title: string;
  country: string;
  genre: string;
  artists: Artist[];
}

export interface BackendArtistResponse {
  artists: Array<{
    id: string;
    name: string;
    image: string;
    popularity: number;
    top_tracks: string[];
    track_details?: Track[];
  }>;
}
