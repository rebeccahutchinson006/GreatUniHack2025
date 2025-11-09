
export interface Artist {
  id?: string;
  name: string;
  imageUrl?: string;
  image?: string;
  topSongs?: string[];
  top_tracks?: string[];
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
  }>;
}
