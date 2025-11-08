
export interface Artist {
  name: string;
  imageUrl: string;
}

export interface MusicSectionData {
  title: string;
  country: string;
  artists: Artist[];
}
