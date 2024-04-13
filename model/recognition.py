import easyocr
import logging


class Recognise(easyocr.Reader):
    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__(
            lang_list=["ru"],
            gpu=True,
        )

    class NoSocialError(Exception):
        def __init__(self) -> None:
            super().__init__("Ценя не является социальной")

    def scan_image(self, path: str):
        result = self.readtext(
            path
        )

        results = [
            {"text": text.lower(), "prob": round(prob, 2), "position": pos}
            for pos, text, prob in result

        ]
        output_name = ""

        confidence_percent = 0.0

        for result in results:
            self.logger.info(
                f"Распознанные данные: {result['text']=} => {result['prob']=}"
            )
            confidence_percent += result["prob"]

            if result["text"].endswith("цена"):
                if result["text"].startswith("соци"):
                    continue
                else:
                    self.logger.error(
                        "Товар не социальный"
                    )
                    raise self.NoSocialError()

            if result["text"].isdigit():
                continue

            if result["prob"] > 0.9:
                output_name += f' {result["text"]}'

        output_price = self.price_calc(results)

        self.logger.info("Ценник успешно распознан")

        return {
            "itemName": output_name,
            "itemPrice": output_price,
            "confidencePercent": round(confidence_percent / len(results), 2)
        }

    def price_calc(self, recognised_data: list[dict]):
        index = 0

        recognised_data = [i for i in recognised_data if i["prob"] > 0.8]

        for data in recognised_data:
            if (" ру" in " " + data["text"] + " " or " руб" in " " + data["text"] + " ") and data["prob"] > 0.9:
                index = recognised_data.index(data)

        probably_price = recognised_data[index - 1]
        probably_price_2 = recognised_data[index - 2]

        if not probably_price["text"].isdigit() or not probably_price_2["text"].isdigit():
            raise self.RecognisePriceError()

        probably_price_height = probably_price["position"][2][0] - probably_price["position"][0][0]
        probably_price_2_height = probably_price_2["position"][2][0] - probably_price_2["position"][0][0]

        rubles = 0
        kopeks = 0

        if probably_price_height > probably_price_2_height:
            rubles = int(probably_price["text"])
            kopeks = int(probably_price_2["text"])
        else:
            rubles = int(probably_price_2["text"])
            kopeks = int(probably_price["text"])

        return f"{rubles}.{kopeks}"

    class RecognisePriceError(Exception):
        def __init__(self) -> None:
            super().__init__("Ошибка распознавания цены")