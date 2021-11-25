import { Directive, Input, Output, EventEmitter, HostListener } from '@angular/core';

@Directive({
  selector: '[copy-clipboard]'
})
export class CopyClipboardDirective {

  @Input('copy-clipboard') public payload: string;

  @Output('copied') public copied: EventEmitter<string> = new EventEmitter<string>();

  @HostListener('click', ['$event']) public onClick(e: MouseEvent): void {
    e.preventDefault();

    if (!this.payload) {
      return;
    }

    let listener = (event: ClipboardEvent) => {
      let clipboard = event.clipboardData;
      clipboard.setData('text', this.payload.toString());
      event.preventDefault();

      this.copied.emit(this.payload);
    }

    document.addEventListener('copy', listener, false);
    document.execCommand('copy');
    document.removeEventListener('copy', listener, false);
  }

}
