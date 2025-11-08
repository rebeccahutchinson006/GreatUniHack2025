
export interface Artist {
  name: string;
  imageUrl: string;
  topSongs: string[];
}

export interface MusicSectionData {
  title: string;
  country: string;
  artists: Artist[];
}
