// play_mod.c: Simple SDL2 module player with visualizer
// https://x.com/mmoroca + Copilot MAY 2025
#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <xmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int paused = 0;
static int stopped = 0;

void fill_audio(void *udata, Uint8 *stream, int len) {
    if (stopped) {
        memset(stream, 0, len);
        return;
    }
    if (!paused) {
        xmp_play_buffer(udata, stream, len, 0);
    } else {
        memset(stream, 0, len);
    }
}

// Helper to render text to the SDL surface
void render_text(SDL_Surface *screen, TTF_Font *font, int x, int y, const char *text, SDL_Color color) {
    SDL_Surface *text_surface = TTF_RenderUTF8_Blended(font, text, color);
    if (text_surface) {
        SDL_Rect dest = {x, y, 0, 0};
        SDL_BlitSurface(text_surface, NULL, screen, &dest);
        SDL_FreeSurface(text_surface);
    }
}

int main(int argc, char **argv) {
    char modfile[1024] = {0};

    if (argc >= 2) {
        strncpy(modfile, argv[1], sizeof(modfile)-1);
    }

    if (SDL_Init(SDL_INIT_AUDIO | SDL_INIT_VIDEO) < 0) {
        fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
        return 1;
    }

    if (TTF_Init() < 0) {
        fprintf(stderr, "TTF_Init: %s\n", TTF_GetError());
        SDL_Quit();
        return 1;
    }

    TTF_Font *font = TTF_OpenFont("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", 14);
    // TTF_Font *font = TTF_OpenFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16);
    // TTF_Font *font = TTF_OpenFont("PressStart2P-Regular.ttf", 12); // Use your downloaded font and a small size

    if (!font) {
        fprintf(stderr, "TTF_OpenFont: %s\n", TTF_GetError());
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    SDL_Window *window = SDL_CreateWindow("Module Player", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 480, 180, SDL_WINDOW_SHOWN);
    if (!window) {
        fprintf(stderr, "SDL_CreateWindow: %s\n", SDL_GetError());
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        return 1;
    }

    // Set window icon
    // SDL_Surface *icon = SDL_LoadBMP("icon.bmp");
    // if (icon) {
    //     SDL_SetWindowIcon(window, icon);
    //     SDL_FreeSurface(icon);
    // } else {
    //     fprintf(stderr, "Warning: Could not load icon.bmp for window icon.\n");
    // }

    SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Surface *screen = SDL_GetWindowSurface(window);

    SDL_Event event;
    int file_loaded = 0;
    xmp_context ctx = NULL;
    struct xmp_module_info mi;

    // Enable drag-and-drop events
    SDL_EventState(SDL_DROPFILE, SDL_ENABLE);

    while (!file_loaded) {
        // Show a message
        SDL_FillRect(screen, NULL, SDL_MapRGB(screen->format, 0, 0, 0));
        render_text(screen, font, 100, 80, "Drag and drop a module file to play", (SDL_Color){255,255,255,0});
        SDL_UpdateWindowSurface(window);

        while (SDL_WaitEvent(&event)) {
            if (event.type == SDL_QUIT) {
                TTF_CloseFont(font);
                TTF_Quit();
                SDL_DestroyRenderer(renderer);
                SDL_DestroyWindow(window);
                SDL_Quit();
                return 0;
            } else if (event.type == SDL_DROPFILE) {
                strncpy(modfile, event.drop.file, sizeof(modfile)-1);
                SDL_free(event.drop.file);
                file_loaded = 1;
                break;
            }
        }
        if (modfile[0]) break;
    }

    // Now load and play the module as before
    ctx = xmp_create_context();
    if (ctx == NULL) {
        fprintf(stderr, "Failed to create xmp context\n");
        return 1;
    }

    if (xmp_load_module(ctx, modfile) < 0) {
        fprintf(stderr, "Failed to load module: %s\n", modfile);
        xmp_free_context(ctx);
        return 1;
    }

    xmp_get_module_info(ctx, &mi);

    SDL_AudioSpec spec;
    spec.freq = 44100;
    spec.format = AUDIO_S16;
    spec.channels = 2;
    spec.samples = 4096;
    spec.callback = fill_audio;
    spec.userdata = ctx;

    if (SDL_OpenAudio(&spec, NULL) < 0) {
        fprintf(stderr, "SDL_OpenAudio: %s\n", SDL_GetError());
        SDL_FreeSurface(screen);
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        xmp_release_module(ctx);
        xmp_free_context(ctx);
        return 1;
    }

    if (xmp_start_player(ctx, 44100, 0) < 0) {
        fprintf(stderr, "xmp_start_player failed\n");
        SDL_CloseAudio();
        SDL_FreeSurface(screen);
        TTF_CloseFont(font);
        TTF_Quit();
        SDL_Quit();
        xmp_release_module(ctx);
        xmp_free_context(ctx);
        return 1;
    }

    SDL_PauseAudio(0);

    struct xmp_frame_info fi;
    int done = 0;
    int last_pattern = -1;
    char info[256];
    SDL_Color white = {255, 255, 255, 0};
    SDL_Color blue = {0, 128, 255, 0};
    SDL_Color yellow = {255, 255, 0, 0};
    SDL_Color red = {255, 0, 0, 0};
    int show_visualizer = 0; // 0: show song info, 1: show visualizer

    while (!done) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                done = 1;
                stopped = 1;
            } else if (event.type == SDL_KEYDOWN) {
                if (event.key.keysym.sym == SDLK_SPACE) {
                    paused = !paused;
                } else if (event.key.keysym.sym == SDLK_ESCAPE) {
                    stopped = 1;
                    done = 1;
                } else if (event.key.keysym.sym == SDLK_v) {
                    show_visualizer = !show_visualizer;
                }
            } else if (event.type == SDL_DROPFILE) {
                // Stop current playback and clean up
                stopped = 1;
                SDL_PauseAudio(1);
                xmp_end_player(ctx);
                xmp_release_module(ctx);
                xmp_free_context(ctx);
                SDL_CloseAudio();

                // Load new file
                strncpy(modfile, event.drop.file, sizeof(modfile)-1);
                SDL_free(event.drop.file);

                ctx = xmp_create_context();
                if (ctx == NULL) {
                    fprintf(stderr, "Failed to create xmp context\n");
                    done = 1;
                    break;
                }
                if (xmp_load_module(ctx, modfile) < 0) {
                    fprintf(stderr, "Failed to load module: %s\n", modfile);
                    xmp_free_context(ctx);
                    done = 1;
                    break;
                }
                xmp_get_module_info(ctx, &mi);

                // Re-open audio
                spec.userdata = ctx;
                if (SDL_OpenAudio(&spec, NULL) < 0) {
                    fprintf(stderr, "SDL_OpenAudio: %s\n", SDL_GetError());
                    xmp_release_module(ctx);
                    xmp_free_context(ctx);
                    done = 1;
                    break;
                }
                if (xmp_start_player(ctx, 44100, 0) < 0) {
                    fprintf(stderr, "xmp_start_player failed\n");
                    SDL_CloseAudio();
                    xmp_release_module(ctx);
                    xmp_free_context(ctx);
                    done = 1;
                    break;
                }
                paused = 0;
                stopped = 0;
                SDL_PauseAudio(0);
            }
        }
        xmp_get_frame_info(ctx, &fi);
        if (fi.loop_count > 0 || stopped) {
            done = 1;
        }

        // Clear screen
        SDL_FillRect(screen, NULL, SDL_MapRGB(screen->format, 0, 0, 0));

        if (!show_visualizer) {
            // --- Song info (blue, field titles white) ---
            int y = 10;
            snprintf(info, sizeof(info), "Title:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %s", mi.mod->name);
            render_text(screen, font, 60, y, info, blue);
            y += 20;
            snprintf(info, sizeof(info), "Type:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %s", mi.mod->type);
            render_text(screen, font, 50, y, info, blue);
            y += 20;
            snprintf(info, sizeof(info), "Channels:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %d", mi.mod->chn);
            render_text(screen, font, 90, y, info, blue);
            y += 20;
            snprintf(info, sizeof(info), "Patterns:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %d", mi.mod->pat);
            render_text(screen, font, 90, y, info, blue);
            y += 20;
            snprintf(info, sizeof(info), "Instruments:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %d", mi.mod->ins);
            render_text(screen, font, 120, y, info, blue);
            y += 20;
            snprintf(info, sizeof(info), "Length:");
            render_text(screen, font, 10, y, info, white);
            snprintf(info, sizeof(info), " %d patterns", mi.mod->len);
            render_text(screen, font, 70, y, info, blue);

            // Controls (two lines, white)
            render_text(screen, font, 10, 140, "SPACE: Play/Pause", white);
            render_text(screen, font, 10, 155, "ESC: Stop and exit   V: Visualizer", white);

            // Pattern info (field title white, value red)
            render_text(screen, font, 300, 140, "Playing pattern:", white);
            snprintf(info, sizeof(info), " %d", fi.pattern);
            render_text(screen, font, 428, 140, info, red);

            // Play/Pause status (white)
            render_text(screen, font, 300, 155, paused ? "Paused" : "Playing", white);

            // --- Channels and notes display (yellow) ---
            static const char *note_names[] = {
                "---", "C-0", "C#0", "D-0", "D#0", "E-0", "F-0", "F#0", "G-0", "G#0", "A-0", "A#0", "B-0",
                "C-1", "C#1", "D-1", "D#1", "E-1", "F-1", "F#1", "G-1", "G#1", "A-1", "A#1", "B-1",
                "C-2", "C#2", "D-2", "D#2", "E-2", "F-2", "F#2", "G-2", "G#2", "A-2", "A#2", "B-2",
                "C-3", "C#3", "D-3", "D#3", "E-3", "F-3", "F#3", "G-3", "G#3", "A-3", "A#3", "B-3",
                "C-4", "C#4", "D-4", "D#4", "E-4", "F-4", "F#4", "G-4", "G#4", "A-4", "A#4", "B-4",
                "C-5", "C#5", "D-5", "D#5", "E-5", "F-5", "F#5", "G-5", "G#5", "A-5", "A#5", "B-5",
                "C-6", "C#6", "D-6", "D#6", "E-6", "F-6", "F#6", "G-6", "G#6", "A-6", "A#6", "B-6",
                "C-7", "C#7", "D-7", "D#7", "E-7", "F-7", "F#7", "G-7", "G#7", "A-7", "A#7", "B-7",
                "C-8"
            };
            int max_channels = mi.mod->chn < 8 ? mi.mod->chn : 8;
            for (int ch = 0; ch < max_channels; ++ch) {
                int note = fi.channel_info[ch].note;
                int ins = fi.channel_info[ch].instrument;
                const char *note_str = (note > 0 && note < (int)(sizeof(note_names)/sizeof(note_names[0]))) ? note_names[note] : "---";
                snprintf(info, sizeof(info), "Ch%02d: %s Ins:%02d", ch+1, note_str, ins);
                render_text(screen, font, 300, 10 + ch * 15, info, yellow);
            }
        } else {
            // --- Simple Visualizer ---
            //render_text(screen, font, 10, 10, "Simple Visualizer (press V for info)", blue);

            int max_channels = mi.mod->chn;
            int visualizer_width = 480 - 60; // leave some margin on both sides
            int base_x = 30, base_y = 10, bar_max_height = 110;
            int spacing = 2;
            int bar_width = (visualizer_width - (max_channels - 1) * spacing) / max_channels;
            if (bar_width < 2) bar_width = 2; // minimum width for visibility

            for (int ch = 0; ch < max_channels; ++ch) {
                int vol = fi.channel_info[ch].volume; // 0-64
                int bar_height = (vol * bar_max_height) / 64;
                SDL_Rect bar = {
                    base_x + ch * (bar_width + spacing),
                    base_y + (bar_max_height - bar_height),
                    bar_width,
                    bar_height
                };
                Uint32 color = SDL_MapRGB(screen->format, 255, 255, 0); // yellow
                SDL_FillRect(screen, &bar, color);

                // Draw channel number just below the bar, above controls
                snprintf(info, sizeof(info), "%d", ch + 1);
                render_text(
                    screen, font,
                    base_x + ch * (bar_width + spacing),
                    base_y + bar_max_height + 5,
                    info, white
                );
            }
            // Controls
            /*
            render_text(screen, font, 10, 160, "SPACE: Play/Pause   ESC: Stop   V: Info", white);
            render_text(screen, font, 250, 160, "Pattern:", white);
            snprintf(info, sizeof(info), " %d", fi.pattern);
            render_text(screen, font, 320, 160, info, red);
            render_text(screen, font, 380, 160, paused ? "Paused" : "Playing", white);
            */
            render_text(screen, font, 10, 140, "SPACE: Play/Pause", white);
            render_text(screen, font, 10, 155, "ESC: Stop and exit   V: Visualizer", white);
            render_text(screen, font, 300, 140, "Playing pattern:", white);
            snprintf(info, sizeof(info), " %d", fi.pattern);
            render_text(screen, font, 428, 140, info, red);
            render_text(screen, font, 300, 155, paused ? "Paused" : "Playing", white);
        }

        SDL_UpdateWindowSurface(window);
        SDL_Delay(20);
    }

    SDL_PauseAudio(1);
    xmp_end_player(ctx);
    xmp_release_module(ctx);
    xmp_free_context(ctx);
    SDL_CloseAudio();
    SDL_FreeSurface(screen);
    TTF_CloseFont(font);
    TTF_Quit();
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}